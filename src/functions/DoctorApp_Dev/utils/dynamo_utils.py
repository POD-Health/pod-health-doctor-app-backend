import boto3

class DynamoDBTable:
    def __init__(self, table_name):
        """
        Initializes the DynamoDB table using a constant table name.

        :param table_name: The name of the DynamoDB table.
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def put_item(self, item):
        """
        Puts an item into the DynamoDB table.

        :param item: The item to put into the table.
        :return: Response from DynamoDB.
        """
        return self.table.put_item(Item=item)

    def get_item(self, key):
        """
        Gets an item from the DynamoDB table by its key.

        :param key: The primary key of the item to retrieve.
        :return: Response from DynamoDB.
        """
        return self.table.get_item(Key=key)

    def query(self, **kwargs):
        """
        Queries the DynamoDB table with support for all query parameters.
        
        :param kwargs: Query parameters including KeyConditionExpression, 
                     IndexName, FilterExpression, etc.
        :return: Response from DynamoDB.
        """
        return self.table.query(**kwargs)

    def scan(self, filter_expression=None):
        """
        Scans the DynamoDB table, optionally with a filter expression.

        :param filter_expression: Optional FilterExpression for the scan.
        :return: Response from DynamoDB.
        """
        if filter_expression:
            return self.table.scan(FilterExpression=filter_expression)
        return self.table.scan()