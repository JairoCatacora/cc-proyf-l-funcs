const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
    try {
        const tenant_id = event.query.tenant_id;
        const user_id = event.query.user_id;

        if (!tenant_id || !user_id) {
            return {
                statusCode: 400,
                body: { message: "tenant_id y user_id son obligatorios" },
            };
        }

        const params = {
            TableName: "pf_orders",
            IndexName: "tenant_id-user_id-index",
            KeyConditionExpression: "tenant_id = :tenant_id AND user_id = :user_id",
            ExpressionAttributeValues: {
                ":tenant_id": tenant_id,
                ":user_id": user_id,
            },
        };

        const result = await dynamo.send(new QueryCommand(params));

        if (result.Items && result.Items.length > 0) {
            return {
                statusCode: 200,
                body: result.Items,
            };
        } else {
            return {
                statusCode: 404,
                body: { 
                    message: "No se encontraron órdenes para este usuario" 
                }
            };
        }
    } catch (error) {
        console.error("Error al listar órdenes:", error);
        return {
            statusCode: 500,
            body: { message: `Error al listar órdenes: ${error.message}` }
        };
    }
};
