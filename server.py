

# from tools.textract_tool import extract_text_from_pdf


# if __name__ == "__main__":
#     text = extract_text_from_pdf("test.pdf")
#     print(text)






from mcp.server.fastmcp import FastMCP
from tools.textract_tool import extract_text_from_pdf

# Create MCP server
mcp = FastMCP("Textract OCR MCP Server")

# Expose tool
@mcp.tool(
    description=(
        "Extract text from an S3 PDF. Pass just the file name like 'invoice.pdf' if it lives "
        "in the 'voice/' prefix (s3://<bucket>/voice/<file>), or pass a full S3 key like "
        "'folder/document.pdf'. Returns the extracted OCR text."
    )
)
def ocr_from_s3_pdf(file_name: str) -> str:
    """
    Takes a PDF file name stored in S3 under voice/ folder
    Returns extracted OCR text using AWS Textract
    """
    return extract_text_from_pdf(file_name)

# IMPORTANT:
# Expose MCP as an ASGI app (HTTP / SSE compatible)
app = mcp.sse_app()

# Run the ASGI app with Uvicorn so SSE is available at /sse
if __name__ == "__main__":
    import os
    import uvicorn

    host = os.environ.get("MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_PORT", "8975"))

    print(f"✅ MCP Textract Server is running and waiting for agent at http://{host}:{port}/sse ...")
    uvicorn.run(app, host=host, port=port, log_level="info")
