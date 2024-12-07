const { S3Client, ListObjectsV2Command } = require("@aws-sdk/client-s3");
const BUCKET_NAME = "prod-productos-ecommerce";
const s3 = new S3Client({ region: "us-east-1" });

exports.handler = async () => {
    try {
        const params = {
            Bucket: BUCKET_NAME,
        };

        const response = await s3.send(new ListObjectsV2Command(params));
        const productPhotos = (response.Contents || [])
            .filter((item) => item.Key.endsWith(".svg"))
            .map((item) => ({
                product_id: item.Key.replace(".svg", ""),
                photo_url: `https://${BUCKET_NAME}.s3.us-east-1.amazonaws.com/${item.Key}`
            }));

        return {
            statusCode: 200,
            body: productPhotos
        };
    } catch (error) {
        console.error('Error listing photos:', error);
        return {
            statusCode: 500,
            body: { error: 'Error retrieving product photos' }
        };
    }
};
