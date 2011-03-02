--
-- Table structure for table 'metrics'
--
-- by Mark Fink, August 2010
--


DROP TABLE IF EXISTS "metrics";
CREATE TABLE "metrics" (
  "project"   text,
  "revision"  integer,
  "file"      text,
  "language"  text,
  "mccabe"    integer,
  "sloc"      integer,
  "comments"  integer,
  "ratio_comment_to_code" real,
  PRIMARY KEY (project, revision, file)
);


