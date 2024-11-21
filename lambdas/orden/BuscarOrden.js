const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    const { tenant_id, order_id } = JSON.parse(event.body);

    const orderParams = {
        TableName: 't_orders',
        Key: { tenant_id, order_id }
    };

    const orderResponse = await dynamodb.get(orderParams).promise();
    const order = orderResponse.Item;

    if (!order) {
        return {
            statusCode: 404,
            body: JSON.stringify({ message: 'Order not found' })
        };
    }

    if (order.order_info && order.order_info.lista_productos) {
        for (const producto of order.order_info.lista_productos) {
            const productoId = producto.producto_id;

            const productParams = {
                TableName: 't_productos',
                Key: {
                    tenant_id,
                    producto_id: productoId
                }
            };

            const productResponse = await dynamodb.get(productParams).promise();
            const productDetails = productResponse.Item;

            if (productDetails) {
                producto.product_info = {
                    name: productDetails.name,
                    category: productDetails.category,
                    price: productDetails.price,
                    image: productDetails.image,
                    detalles: productDetails.detalles || {}
                };
            }
        }
    }

    return {
        statusCode: 200,
        body: JSON.stringify(order)
    };
};
