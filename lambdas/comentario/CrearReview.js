const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const {tenant_id, product_id, review_id, user_id, comment, stars} = body

    const lastModification = new Date().toISOString();

    await dynamo.send(
      new PutCommand({
        TableName: "pf_comentarios",
        Item: {
          tenant_id: tenant_id,
          pr_id: `${product_id}#${review_id}`,
          product_id: product_id,
          review_id: review_id,
          user_id: user_id,
          tp_id: `${tenant_id}#${product_id}`,
          comment: comment,
          stars: Number(stars),
          last_modification:lastModification
        },
      })
    );

    return {
      statusCode: 201,
      body: {
        message: "Inventory created successfully",
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while creating the inventory",
      },
    };
  }
};
