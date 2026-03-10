const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;
const API_GATEWAY_URL = process.env.API_GATEWAY_URL || "http://api-gateway:8080";

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.use(
  "/api",
  createProxyMiddleware({
    target: API_GATEWAY_URL,
    changeOrigin: true,
  })
);

app.use(express.static(path.join(__dirname, "public")));

app.listen(PORT, () => {
  console.log(`Frontend server listening on port ${PORT}`);
  console.log(`API proxy target: ${API_GATEWAY_URL}`);
});
