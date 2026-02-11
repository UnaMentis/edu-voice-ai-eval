-- Add download tracking columns to eval_models
ALTER TABLE eval_models ADD COLUMN download_status TEXT NOT NULL DEFAULT 'none';
ALTER TABLE eval_models ADD COLUMN local_path TEXT;
ALTER TABLE eval_models ADD COLUMN download_error TEXT;
ALTER TABLE eval_models ADD COLUMN download_progress REAL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_eval_models_download_status ON eval_models(download_status);
