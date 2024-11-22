const AWS = require('aws-sdk');
const dynamoDB = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    const userId = event.queryStringParameters.user_id;

    const params = {
        TableName: 't_pagos',
        KeyConditionExpression: 'user_id = :user_id',
        ExpressionAttributeValues: {
            ':user_id': userId
        }
    };

    try {
        // Obtener los pagos desde la tabla DynamoDB para el user_id proporcionado
        const data = await dynamoDB.query(params).promise();

        // Devolver la lista de pagos realizados
        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Historial de pagos recuperado exitosamente',
                pagos: data.Items
            })
        };
    } catch (error) {
        // En caso de error, devuelve un mensaje de error
        return {
            statusCode: 500,
            body: JSON.stringify({
                message: 'Error al recuperar el historial de pagos',
                error: error.message
            })
        };
    }
};
