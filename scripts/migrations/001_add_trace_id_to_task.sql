-- Migration: Add trace_id to Task
-- Description: Adds the OpenTelemetry trace_id column to the Task table for reasoning tracing.

ALTER TABLE task ADD COLUMN IF NOT EXISTS trace_id VARCHAR;
