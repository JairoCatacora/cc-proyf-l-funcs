const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const tenant_id = event.query.tenant_id;
    const userId = event.query.userId;

    if (!tenant_id || !userId) {
      return {
        statusCode: 400,
        body: {
          message: "tenant_id and userId are required",
        },
      };
    }

    const params = {
      TableName: "pf_pagos",
      KeyConditionExpression: "tenant_id = :tenant_id AND user_id = :user_id",
      ExpressionAttributeValues: {
        ":tenant_id": tenant_id,
        ":user_id": userId,
      },
    };

    const data = await dynamo.send(
        new QueryCommand({
            TableName: "t_pagos",
            KeyConditionExpression: "tenant_id = :tenant_id AND user_id = :user_id",
            ExpressionAttributeValues: {
                ":tenant_id": tenant_id,
                ":user_id": userId,
            },
        })
    );

    if (response.Items && response.Items.length > 0) {
        return {
          statusCode: 200,
          body: data.Items
        };
      } else {
        return {
          statusCode: 404,
          body: {
            message: "No products found for the given tenant_id",
            body: data.Items || [],
          }
        };
      }
  } catch (error) {
    console.error("Error al recuperar el historial de pagos:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: error.message || "Error al recuperar el historial de pagos"
      }),
    };
  }
};
