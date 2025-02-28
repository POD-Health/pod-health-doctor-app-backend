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
        return self.table.put_item(Item=item)

    def get_item(self, key):
        return self.table.get_item(Key=key)

    def query(self, key_condition):
        return self.table.query(KeyConditionExpression=key_condition)

    def scan(self, filter_expression=None):
        if filter_expression:
            return self.table.scan(FilterExpression=filter_expression)
        return self.table.scan()
