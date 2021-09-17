import logging
from datetime import datetime
from io import StringIO

import urllib3
import requests

import sqlalchemy
import pandas as pd

from django.conf import settings
from django.db import models
from .models import Customer, Contragent, ThrukHost  # noqa: F401

logger = logging.getLogger(__name__)

driver = "ODBC Driver 17 for SQL Server"

# External databases
SOURCE_USER = "mongrf"
SOURCE_PWD = "UUz77LkAxhq5#s8JNezEhZ"

# MCS database params
mcs_user = settings.DATABASES["default"]["USER"]
mcs_password = settings.DATABASES["default"]["PASSWORD"]
mcs_db = settings.DATABASES["default"]["NAME"]
mcs_db_host = settings.DATABASES["default"]["HOST"]

# Request settings
HEADERS = {
    "X-Thruk-Auth-Key": "51eeb551b4e51bbeb6bfdfc98f6a8e650790c0fe6d3b4108b160758d9059e6b3_1"
}
THRUK_ROOT_URL = "https://ostmon.dtln.local/thruk/r/csv/"
# Connection settings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def value_to_sql_string_format(value):
    """Convert value to PostgreSQL SQL statement string format

    Args:
        value (Any): Input value

    Returns:
        String: String value representation for update sql statement in PostgreSQL dialect
    """
    datatype = type(value).__name__
    if "bool" in datatype:
        str_value = str(value)
    elif "float" in datatype or "int" in datatype:
        str_value = str(value)
        if str_value == "nan":
            str_value = "null"
    elif "str" in datatype or "Timestamp" in datatype or "object" in datatype:
        if value == "None":
            str_value = "null"
        else:
            # We escape single quote and duplicate percent sign for psycopg2
            str_value = "'" + str(value).replace("'", "''").replace("%", "%%") + "'"
    elif "NoneType" in datatype:
        str_value = "null"
    elif "NaTType" in datatype:
        str_value = "null"
    else:
        str_value = "'" + str(value) + "'"
    return str_value


def dtln_data2df(source_server, source_db, sql_statement, data_types, mcs_model):
    """Get data from the source MS SQL Server database and return DataFrame data

    Args:
        source_server (String): MS SQL Server address
        source_db (String): Database name
        sql_statement (String): SQL Select statement
        data_types (Dict): DataFrame column names with data types
        mcs_model (String): Corresponding Django model name

    Returns:
        DataFrame: Result DataFrame
    """
    # Set source DB connection for SQL Alchemy
    source_engine = sqlalchemy.create_engine(
        "mssql+pyodbc://"
        + SOURCE_USER
        + ":"
        + SOURCE_PWD
        + "@"
        + source_server
        + "/"
        + source_db
        + "?driver="
        + driver,
        echo=False,
        encoding="utf8",
        connect_args={"timeout": 3},
    )
    # Read source data
    source_df = pd.read_sql_query(
        sql_statement, dtype=data_types, index_col="id", con=source_engine
    )

    # Convert local MSK 'naive' timestamp to UTC format with Time Zone
    if "archived_datetime" in source_df.columns:
        source_df = source_df.copy()
        source_df["archived_datetime"] = source_df["archived_datetime"].dt.tz_localize(
            "Europe/Moscow"
        )

    read_rows_count = len(source_df.index)
    logger.info(f"{read_rows_count} rows fetched from {source_db}")

    # Add row for Unknown object. It is used as unknown foreign key
    if "int" in str(source_df.index.dtype):
        source_df.loc[0, ["name", "archived"]] = [
            "Empty " + mcs_model,
            True,
        ]
    elif "object" in str(str(source_df.index.dtype)):
        source_df.loc["0", ["name", "archived"]] = [
            "Empty " + mcs_model,
            True,
        ]

    # Add row for incorrect object. It is used as incorrect foreign key
    if "int" in str(source_df.index.dtype):
        source_df.loc[-1, ["name", "archived"]] = [
            "Incorrect " + mcs_model,
            True,
        ]
    elif "object" in str(str(source_df.index.dtype)):
        source_df.loc["-1", ["name", "archived"]] = [
            "Incorrect " + mcs_model,
            True,
        ]
    source_engine.dispose()
    return source_df


def get_rest_api_response(request_url):
    """Make REST API HTTP GET request and return result text data

    Args:
        request_url (String): Requested URL

    Returns:
        String: Result text data
    """
    logger.info(f"Making Thruk REST API request with url: {request_url}")
    try:
        req_res = requests.get(request_url, headers=HEADERS, verify=False, timeout=60)
    except requests.exceptions.HTTPError as errh:
        logger.error("HTTP Error: " + str(errh))
    except requests.exceptions.ConnectionError as errc:
        logger.error("Error Connecting: " + str(errc))
    except requests.exceptions.Timeout as errt:
        logger.error("Timeout Error: " + str(errt))
    except requests.exceptions.RequestException as err:
        logger.error("Oops: Something Else: " + str(err))
    else:
        if req_res.status_code == 200:
            result_text = req_res.text.rstrip()
            return result_text
        else:
            logger.error(
                "Incorrect Thruk response: Status Code "
                + str(req_res.status_code)
                + " - "
                + req_res.text
            )
    return ""


def thruk_request2df(records_filter, record_attrs, column_names):
    """Construct URL, make request to Thruk REST API and return Dataframe.

    Args:
        records_filter (String): Part of Thruk REST API URL with Nagios objects (Hosts, Services, Commands, etc) filter
        record_attrs (List): List of requested Nagios object attributes
        column_names (List): List of DataFrame columns names

    Returns:
        DataFrame: Nagios objects DataFrame with attributes
    """
    thruk_rest_api_url = (
        THRUK_ROOT_URL + records_filter + "&columns=" + ",".join(record_attrs)
    )
    csv_out = get_rest_api_response(thruk_rest_api_url)

    # Convert Thruk REST API csv response to Pandas DataFrame
    if csv_out:
        csv_file = StringIO(csv_out)
        df = pd.read_csv(csv_file, sep=";", names=column_names)

        # Add Index column for DataFrame
        if "hosts" in records_filter:
            df["id"] = (df["peer_name"] + "+" + df["name"]).str.upper()

        if "services" in records_filter:
            df["id"] = (
                df["peer_name"] + "+" + df["host_name"] + "+" + df["description"]
            ).str.upper()
            df["thruk_host_id"] = (df["peer_name"] + "+" + df["host_name"]).str.upper()

        # TODO: add index modification for duplicated indexes. It is actual for Nagios Services

        df.set_index("id", inplace=True)
        thruk_objects_count = len(df.index)
        logger.info(f"{thruk_objects_count} objects returned from Thruk REST API")
    else:
        df = pd.DataFrame(columns=column_names)
        logger.warning("Empty responce returned from Thruk REST API")
    return df


def create_checked_foreign_key_df(source_fk_df, mcs_model):
    """Process Foreing Key check in source_fk_df for mcs_model

    Args:
        source_fk_df (DataFrame): DataFrame contains single column with source data to check for correct foreign key.
        mcs_model (String): Corresponding Django model name

    Returns:
        DataFrame: DataFrame with single foreign key check result column.
    """
    # Get table name and index for foreign key in source_fk_df
    source_column_name = list(source_fk_df.columns)[0]
    checked_column_name = source_column_name.replace("_source", "_checked_id")
    fk_model = eval(
        mcs_model
        + "._meta.get_field('"
        + checked_column_name
        + "').remote_field.model.__name__"
    )

    # Create keys dataframe
    key_values_list = list(eval(fk_model + ".objects.values_list('pk', flat=True)"))
    keys_df = pd.DataFrame(key_values_list, columns=["id"])

    # Build DataFrame with key check result
    check_fk_df = source_fk_df.merge(
        keys_df,
        how="left",
        left_on=source_column_name,
        right_on="id",
        suffixes=("", "_y"),
        indicator=True,
    )

    # Copy all values to new column
    check_fk_df[checked_column_name] = check_fk_df[source_column_name]

    # Modify incorrect or empty values
    if "int" in str(keys_df["id"].dtype):
        check_fk_df.loc[check_fk_df["_merge"] == "left_only", checked_column_name] = -1
        check_fk_df.loc[
            (check_fk_df["_merge"] == "left_only")
            & (
                check_fk_df[source_column_name].isnull()
                | check_fk_df[source_column_name].isna()
            ),
            checked_column_name,
        ] = 0
    elif "object" in str(keys_df["id"].dtype):
        check_fk_df.loc[
            check_fk_df["_merge"] == "left_only", checked_column_name
        ] = "-1"
        check_fk_df.loc[
            (check_fk_df["_merge"] == "left_only")
            & (
                check_fk_df[source_column_name].isnull()
                | check_fk_df[source_column_name].isna()
            ),
            checked_column_name,
        ] = "0"

    # Return result DataFrame
    result_df = check_fk_df[checked_column_name]
    return result_df


def df2mcs(source_df, mcs_model):
    """Find and fix FK violations, check if data changed, insert or update data in MCS table

    Args:
        source_df (DataFrame): DataFrame with current data from source
        mcs_model (String): Corresponding Django model name
    """
    # Get fk fields
    model_fields = eval(mcs_model + "._meta.fields")
    fk_fields = [
        field.name for field in model_fields if isinstance(field, models.ForeignKey)
    ]

    # Create DataFrame with source fk column only for field containing "_checked"
    for fk_field in fk_fields:
        if "_checked" in fk_field:
            source_fk_column = fk_field.replace("_checked", "_source")
            source_fk_df = source_df[[source_fk_column]]
            # Add column with checked foreign keys
            source_df[fk_field + "_id"] = create_checked_foreign_key_df(
                source_fk_df, mcs_model
            ).values

    # Set MCS connection for SQL Alchemy
    mcs_engine = sqlalchemy.create_engine(
        "postgresql+psycopg2://"
        + mcs_user
        + ":"
        + mcs_password
        + "@"
        + mcs_db_host
        + "/"
        + mcs_db,
        echo=False,
        encoding="utf8",
        connect_args={"connect_timeout": 1},
    )

    # Get table name using model metadata
    mcs_table = eval(mcs_model + ".objects.model._meta.db_table")

    # Read MCS table
    mcs_table_df = pd.read_sql_table(mcs_table, index_col="id", con=mcs_engine)
    mcs_table_rows_count = len(mcs_table_df.index)
    logger.info(f"MCS table {mcs_table} contains {mcs_table_rows_count} rows")

    # Check difference between source and MCS data
    source_columns = list(source_df.columns)
    check_diff_df = source_df.merge(
        mcs_table_df, how="outer", on="id", suffixes=("", "_y"), indicator=True
    )

    # New records
    new_records_df = check_diff_df.loc[check_diff_df["_merge"] == "left_only"][
        source_columns
    ]
    new_records_count = 0 if new_records_df.empty else len(new_records_df.index)
    logger.info(f"Found {new_records_count} new records for {mcs_table}")

    # Deleted records
    deleted_records_df = check_diff_df.loc[check_diff_df["_merge"] == "right_only"][
        source_columns
    ]
    deleted_records_count = 0 if deleted_records_df.empty else len(deleted_records_df)
    logger.info(f"Found {deleted_records_count} deleted records for {mcs_table}")

    # Equal or updated records
    equal_or_updated_records_df = check_diff_df.loc[check_diff_df["_merge"] == "both"][
        source_columns
    ]
    equal_or_updated_records_cound = (
        0
        if equal_or_updated_records_df.empty
        else len(equal_or_updated_records_df.index)
    )
    logger.info(
        f"Found {equal_or_updated_records_cound} equal or updated records for {mcs_table}"
    )

    # Find only updated records
    print(equal_or_updated_records_df.dtypes)
    print(mcs_table_df.dtypes)
    check_updated_records_df = equal_or_updated_records_df.reset_index(level=0).merge(
        mcs_table_df, how="left", on=source_columns, indicator=True
    )
    updated_records_df = check_updated_records_df.loc[
        check_updated_records_df["_merge"] == "left_only"
    ][source_columns + ["id"]].set_index("id")
    updated_records_cound = (
        0 if updated_records_df.empty else len(updated_records_df.index)
    )
    logger.info(f"Found {updated_records_cound} updated records for {mcs_table}")

    # Insert new records
    new_records_df.to_sql(
        name=mcs_table,
        con=mcs_engine,
        if_exists="append",
    )
    logger.info(f"Added {new_records_count} new records to {mcs_table}")

    # Update updated (differed) records
    with mcs_engine.begin() as conn:
        for row_id, row in updated_records_df.iterrows():
            update_statement = "update " + mcs_table + " set "
            for column in source_columns:
                update_statement = (
                    update_statement
                    + column
                    + " = "
                    + value_to_sql_string_format(row[column])
                    + ", "
                )
            update_statement = (
                update_statement.rstrip(", ")
                + " where id = "
                + value_to_sql_string_format(row_id)
            )
            conn.execute(update_statement)
    logger.info(f"{updated_records_cound} records updated in {mcs_table}")

    # Mark deleted records as archived
    with mcs_engine.begin() as conn:
        for row_id, _row in deleted_records_df.iterrows():
            update_statement = (
                "update "
                + mcs_table
                + " set archived = True, archived_datetime = '"
                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                + "' where id = "
                + value_to_sql_string_format(row_id)
            )
            conn.execute(update_statement)
    logger.info(
        f"{deleted_records_count} deleted records marked as archived in {mcs_table}"
    )

    mcs_engine.dispose()
