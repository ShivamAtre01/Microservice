// Adjust these if you're not running via docker-compose on localhost,
// e.g. point them at your EKS Ingress hostname later.
const CONFIG = {
    USER_SERVICE_URL: "http://108.130.20.168:5001",
    ORDER_SERVICE_URL: "http://108.130.20.168:5000",
    PAYMENT_SERVICE_URL: "http://108.130.20.168:5002",
    NOTIFICATION_SERVICE_URL: "http://108.130.20.168:5003"
};
