const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    const { tenant_id, producto_id, product_name, product_brand, product_info, product_price, product_stock } = JSON.parse(event.body);

    const params = {
        TableName: 't_productos',
        Key: { tenant_id, producto_id },
        UpdateExpression: 'SET product_name = :name, product_brand = :brand, product_info = :info, product_price = :price, product_stock = :stock',
        ExpressionAttributeValues: {
            ':name': product_name,
            ':brand': product_brand,
            ':info': product_info,
            ':price': product_price,
            ':stock': product_stock
        },
        ReturnValues: 'UPDATED_NEW'
    };

    const response = await dynamodb.update(params).promise();
    return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Product updated', updatedAttributes: response.Attributes })
    };
};
