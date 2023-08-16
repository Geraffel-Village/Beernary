--
-- Data for table `event`
--

LOCK TABLES `event` WRITE;
INSERT INTO `event` VALUES (1,'event0',1);
UNLOCK TABLES;

--
-- Data for table `keg`
--

LOCK TABLES `keg` WRITE;
INSERT INTO `keg` VALUES
(1,1,50,0,0);
UNLOCK TABLES;

--
-- Data for table `users`
--

LOCK TABLES `users` WRITE;
INSERT INTO `users` VALUES
('42DEADBE', 1 ,'user0','2022-07-24 15:14:10');
UNLOCK TABLES;
