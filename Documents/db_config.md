# mysql user and password

mysql_user: root

mysql_password: 123456

# db 
articles

## table
asahi_rss_articles
```
CREATE TABLE `asahi_rss_articles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `link` varchar(500) NOT NULL,
  `pubDate` datetime NOT NULL,
  `content` text,
  `contentSnippet` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_title_unique` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=2641 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

```
nhk_rss_articles

```
CREATE TABLE `nhk_rss_articles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `link` varchar(500) NOT NULL,
  `pubDate` datetime NOT NULL,
  `content` text,
  `contentSnippet` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_title_unique` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=574 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci


```

wallstreetcn_rss_articles

```
CREATE TABLE `wallstreetcn_rss_articles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `link` varchar(500) NOT NULL,
  `pubDate` datetime NOT NULL,
  `content` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_title_unique` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=503 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

```

wsj_rss_articles

```
CREATE TABLE `wsj_rss_articles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `link` varchar(500) NOT NULL,
  `pubDate` datetime NOT NULL,
  `content` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_title_unique` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=1112 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

```

youtube_rss_articles

```
CREATE TABLE `youtube_rss_articles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `link` varchar(255) NOT NULL,
  `pubDate` datetime NOT NULL,
  `isoDate` datetime NOT NULL,
  `author` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_title_unique` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=2191 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

```

# db

finances

# table

```
CREATE TABLE `stock_indices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `nasdaq` decimal(12,3) NOT NULL,
  `nasdaq_100` decimal(12,3) NOT NULL,
  `nasdaq_100_pe` decimal(12,3) NOT NULL,
  `n225` decimal(12,3) NOT NULL,
  `vix` decimal(12,3) NOT NULL,
  `a` decimal(12,3) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci


```
