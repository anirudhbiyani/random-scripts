CREATE OR REPLACE PROCEDURE CREATE_SERVICE_USER(
    OLD_USERNAME STRING,
    COMMENT_TEXT STRING,
    RSA_PUBLIC_KEY STRING
)
RETURNS STRING
LANGUAGE SQL
    EXECUTE AS CALLER
AS
$$
BEGIN
    -- Set the new username by appending '_SERVICE'
    LET NEW_USERNAME STRING := :OLD_USERNAME || '_SERVICE';
    
    -- Get user details from account_usage
    LET user_details RESULTSET := (
        SELECT name, LOGIN_NAME, DEFAULT_ROLE, DEFAULT_WAREHOUSE 
        FROM snowflake.account_usage.users 
        WHERE name = :OLD_USERNAME AND DELETED_ON IS NULL 
    );
    
    -- Create the new service user with conditional handling for NULL values
    LET create_user_sql STRING := (
        SELECT 'CREATE OR REPLACE USER ' || :NEW_USERNAME || 
               ' TYPE=SERVICE LOGIN_NAME=' || :NEW_USERNAME || 
               CASE 
                   WHEN DEFAULT_WAREHOUSE IS NOT NULL THEN ' DEFAULT_WAREHOUSE=' || DEFAULT_WAREHOUSE 
                   ELSE '' 
               END ||
               CASE 
                   WHEN DEFAULT_ROLE IS NOT NULL THEN ' DEFAULT_ROLE=' || DEFAULT_ROLE 
                   ELSE '' 
               END || 
               ' COMMENT=''' || :COMMENT_TEXT || ''''
        FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
    );
    
    EXECUTE IMMEDIATE :create_user_sql;

    -- Get grants from old user and apply to new user
    LET grant_commands RESULTSET := (
        SELECT 'GRANT ROLE ' || ROLE || ' TO USER ' || :NEW_USERNAME AS SQL_COMMAND
        FROM SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS
        WHERE GRANTEE_NAME = :OLD_USERNAME AND DELETED_ON IS NULL
    );
    
    -- Execute each grant command
    FOR grant_cmd IN grant_commands DO
        EXECUTE IMMEDIATE grant_cmd.SQL_COMMAND;
    END FOR;

    EXECUTE IMMEDIATE 'ALTER USER '  || :NEW_USERNAME || ' SET RSA_PUBLIC_KEY = ''' || :RSA_PUBLIC_KEY || '''';

    -- Prepare return message
    RETURN 'Service user ' || :NEW_USERNAME || ' created successfully with all permissions from ' || :OLD_USERNAME;
END;
$$;

-- Example usage:
-- CALL CREATE_SERVICE_USER(
--     '<OLD_ACCOUNT>',
--     '<JIRA Ticket Reference EN/SSDLC>',
--     'MIIBIj...'  -- Your RSA public key here
-- );