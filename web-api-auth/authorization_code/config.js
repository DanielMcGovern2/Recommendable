// configuring variables from .env...
const dotenv = require('dotenv');
module.exports = {
  cli_id: process.env.CLIENT_ID,
  cli_sec: process.env.CLIENT_SECRET,
  red_uri: process.env.REDIRECT_URI,
  port: process.env.PORT,
  acc_tok: process.env.ACCESS_TOKEN
};