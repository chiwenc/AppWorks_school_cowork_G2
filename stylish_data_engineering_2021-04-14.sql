# ************************************************************
# Sequel Pro SQL dump
# Version 4541
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# Host: 127.0.0.1 (MySQL 5.7.18)
# Database: stylish_data_engineering
# Generation Time: 2021-04-14 09:31:09 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table alembic_version
# ------------------------------------------------------------

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table product
# ------------------------------------------------------------

CREATE TABLE `product` (
  `id` varchar(200) NOT NULL DEFAULT '',
  `category` varchar(127) DEFAULT '',
  `title` varchar(255) DEFAULT '',
  `description` varchar(255) DEFAULT '',
  `price` int(10) unsigned DEFAULT NULL,
  `texture` varchar(127) DEFAULT '',
  `wash` varchar(127) DEFAULT '',
  `place` varchar(127) DEFAULT '',
  `note` varchar(127) DEFAULT '',
  `story` text,
  `main_image` varchar(255) DEFAULT NULL,
  `images` varchar(255) DEFAULT NULL,
  `source` varchar(100) DEFAULT NULL,
  `image_base64` text,
  PRIMARY KEY (`id`),
  KEY `category` (`category`),
  KEY `title` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table rating
# ------------------------------------------------------------

CREATE TABLE `rating` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(127) NOT NULL,
  `item_id` varchar(200) NOT NULL,
  `rating` int(11) NOT NULL,
  `time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table similarity_model
# ------------------------------------------------------------

CREATE TABLE `similarity_model` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `item1_id` varchar(100) DEFAULT NULL,
  `item2_id` varchar(100) DEFAULT NULL,
  `similarity` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `item1_id` (`item1_id`,`item2_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table tracking_analysis
# ------------------------------------------------------------

CREATE TABLE `tracking_analysis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` timestamp NULL DEFAULT NULL,
  `all_user_count` int(11) DEFAULT NULL,
  `active_user_count` int(11) DEFAULT NULL,
  `new_user_count` int(11) DEFAULT NULL,
  `return_user_count` int(11) DEFAULT NULL,
  `view_count` int(11) DEFAULT NULL,
  `view_item_count` int(11) DEFAULT NULL,
  `add_to_cart_count` int(11) DEFAULT NULL,
  `checkout_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table tracking_raw
# ------------------------------------------------------------

CREATE TABLE `tracking_raw` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `request_url` text NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table tracking_realtime
# ------------------------------------------------------------

CREATE TABLE `tracking_realtime` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `client_id` varchar(127) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `event_type` varchar(255) NOT NULL,
  `view_detail` varchar(255) DEFAULT NULL,
  `item_id` int(11) DEFAULT NULL,
  `checkout_step` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table user
# ------------------------------------------------------------

CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(15) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `username` varchar(127) NOT NULL,
  `picture` varchar(255) DEFAULT NULL,
  `access_token` text NOT NULL,
  `access_expire` bigint(20) NOT NULL,
  `login_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table variant
# ------------------------------------------------------------

CREATE TABLE `variant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `color_code` varchar(15) DEFAULT NULL,
  `color_name` varchar(15) DEFAULT NULL,
  `size` varchar(15) DEFAULT NULL,
  `stock` int(11) DEFAULT NULL,
  `product_id` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `variant_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
