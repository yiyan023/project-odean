module.exports = {
  seedDataDir: process.env.SEED_DATA_DIR || '/app/seed_data',
  port: parseInt(process.env.PORT || '5000', 10),
};
