const AWS = require('aws-sdk');

const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        // Asumir que `event.body` ya es un objeto y contiene una lista de pagos
        const body = event.body;

        // Validar que `body.pagos` sea una lista válida
        const pagos = body?.pagos;
        if (!Array.isArray(pagos) || pagos.length === 0) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Invalid request: missing or empty pagos list' })
            };
        }

        const tableName = 't_pagos';
        const resultados = [];

        // Procesar cada pago en la lista
        for (const pago of pagos) {
            const { tenant_id, producto_id, pago_info } = pago;

            // Validar que todos los campos necesarios estén presentes
            if (!tenant_id || !producto_id || !pago_info) {
                resultados.push({
                    tenant_id,
                    producto_id,
                    error: 'Missing required fields'
                });
                continue;
            }

            // Crear el objeto para insertar en DynamoDB
            const params = {
                TableName: tableName,
                Item: {
                    tenant_id,
                    producto_id,
                    pago_info
                }
            };

            try {
                // Insertar el pago en DynamoDB
                await dynamodb.put(params).promise();
                resultados.push({
                    tenant_id,
                    producto_id,
                    message: 'Pago created successfully'
                });
            } catch (error) {
                // Capturar errores específicos para cada pago
                resultados.push({
                    tenant_id,
                    producto_id,
                    error: error.message
                });
            }
        }

        // Devolver el resumen de los resultados
        return {
            statusCode: 201,
            body: JSON.stringify(resultados)
        };

    } catch (error) {
        console.error('Exception:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};
