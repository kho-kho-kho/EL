DROP TABLE IF EXISTS dapi;

CREATE TABLE dapi (
  word TEXT PRIMARY KEY NOT NULL,
  def BLOB NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);