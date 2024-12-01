const { S3Client, ListObjectsV2Command } = require("@aws-sdk/client-s3");
const BUCKET_NAME = "dev-multishop-logos";
const s3 = new S3Client({ region: "us-east-1" });

exports.lambda_handler = async () => {
    try {
        const params = {
            Bucket: BUCKET_NAME,
        };

        const response = await s3.send(new ListObjectsV2Command(params));
        const tenantLogos = (response.Contents || [])
            .filter((item) => item.Key.endsWith(".svg")) // Filtra solo archivos .svg
            .map((item) => ({
                tenant_id: item.Key.replace(".svg", ""),
                logo_url: `https://${BUCKET_NAME}.s3.us-east-1.amazonaws.com/${item.Key}`
            }));

        return {
            statusCode: 200,
            body: JSON.stringify(tenantLogos)
        };
    } catch (error) {
        console.error('Error listing logos:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Error retrieving tenant logos' })
        };
    }
};
