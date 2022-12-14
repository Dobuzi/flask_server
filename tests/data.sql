INSERT INTO user (username, password)
VALUES
	('test', 'pbkdf2:sha256:260000$yv0jzL88mH7ciEVd$b3cf6f097355821f4295a46c507230d4e46f015543768516e06edbc097968ed8'),
	('other', 'pbkdf2:sha256:260000$mIyPMGxG2T2RVABv$1cabd667e5182da68f7a9c3c7a98ccf12ac2e00bda9e7811de18415f1eef9a13');

INSERT INTO post (title, body, author_id, created)
VALUES
	('test title', 'test' || x'0a' || 'body', 1, '2022-12-13 00:00:00');
