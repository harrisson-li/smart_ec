from ectools.config import get_logger, set_environment
from ectools.database_helper import *

logger = get_logger()


def test_fetch_one():
    set_environment('uat')
    sql = "SELECT * FROM oboe.dbo.BookingStatus_lkp"
    row = fetch_one(sql)
    logger.info(row)
    assert row.Name == 'Empty'

    row = fetch_one("SELECT * FROM oboe.dbo.BookingStatus_lkp Where Name = ?", 'Booked', as_dict=True)
    logger.info(row)
    assert row['Name'] == 'Booked'


def test_fetch_all():
    set_environment('uat')
    sql = "SELECT * FROM oboe.dbo.BookingStatus_lkp"
    rows = fetch_all(sql)
    logger.info(rows)
    assert rows[1].Name == "Booked"
    assert len(rows) == 14

    sql = "SELECT * FROM oboe.dbo.ClassCategory_lkp WHERE IsDeleted = ? AND Name=?"
    rows = fetch_all(sql, (0, 'F2F'), as_dict=True)
    logger.info(rows)
    assert len(rows) == 1


def test_execute_query():
    set_environment('uat')
    sql = """
    INSERT INTO [NorthwindCS].[dbo].[Products]
           ([ProductName]
           ,[SupplierID]
           ,[CategoryID]
           ,[QuantityPerUnit]
           ,[UnitPrice]
           ,[UnitsInStock]
           ,[UnitsOnOrder]
           ,[ReorderLevel]
           ,[Discontinued])
     VALUES
           ('Test',1,1,'Test',10.00,1,1,1,1)
    """
    assert execute_query(sql) == 1

    sql = "DELETE FROM NorthwindCS.dbo.Products WHERE ProductName = 'Test'"
    assert execute_query(sql) == 1


def test_connect_db():
    set_environment('uat')
    sql = """
    USE [NorthwindCS]
    DECLARE @ret int
    EXEC @ret=	[dbo].[Sales by Year]
            @Beginning_Date = N'1990-1-1',
            @Ending_Date = N'2000-1-1'
    SELECT @ret
    """
    connect_database()
    get_cursor().execute(sql)
    get_cursor().commit()
    assert get_cursor().rowcount == -1
    close_database()
