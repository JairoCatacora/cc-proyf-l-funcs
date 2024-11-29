const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand } = require("@aws-sdk/lib-dynamodb");
const https = require("https");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

exports.lambda_handler = async (event) => {
  try {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const lastModification = new Date().toISOString();
    const {tenant_id, product_id, review_id, user_id, comment, stars} = body

    if (!tenant_id || !product_id || !review_id || !user_id || comment === undefined || stars === undefined) {
      return {
        statusCode: 400,
        body: { message: "Missing required fields" },
      };
    }

    const params = {
      TableName: "pf_comentario",
      Key: {
        tenant_id: tenant_id,
        pr_id: `${product_id}#${review_id}`,
      },
      UpdateExpression: `
        SET 
        comment = :comment,
        stars = :stars,
        last_modification = :last_modification
      `,
      ExpressionAttributeValues: {
        ":stars": Number(stars),
        ":comment": comment,
        ":last_modification": lastModification,
      },
      ReturnValues: "UPDATED_NEW",
    };

    const updateResponse = await dynamo.send(new UpdateCommand(params));

    return {
      statusCode: 200,
      body: {
        message: "Se actualizó el comentario existosamente",
        updatedAttributes: updateResponse.Attributes,
      },
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while updating the review",
      },
    };
  }
};
