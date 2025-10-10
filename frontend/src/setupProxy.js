const basicAuth = require('basic-auth-connect');

module.exports = function(app) {
    // Protect all routes with username/password
    app.use(basicAuth('aipocadmin', 'info@123'));
};