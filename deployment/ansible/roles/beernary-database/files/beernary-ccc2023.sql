--
-- Dumping data for table `event`
--

LOCK TABLES `event` WRITE;
INSERT INTO `event` VALUES (1,'CCC2023',1);
UNLOCK TABLES;

--
-- Dumping data for table `keg`
--

LOCK TABLES `keg` WRITE;
INSERT INTO `keg` VALUES
(1,1,50,0,1),
(2,1,50,0,1),
(3,1,50,0,1),
(4,1,50,0,1),
(5,1,50,0,0);
UNLOCK TABLES;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
INSERT INTO `users` VALUES
('02004C90CF', 1, 'fuselage','2023-08-14 22:55:16'),
('0200920AA1', 2, 'Test-Tag','2022-07-24 13:14:10'),
('03004B84A7', 1, 'sammys','2023-08-14 22:56:13'),
('2A000DD7EC', 1, 'gramels','2023-08-14 22:55:24'),
('2F00BF4A54', 1, 'chaosle','2023-08-14 22:55:33'),
('2F00BFB889', 1, 'Cyberkai','2023-08-14 22:55:47'),
('3100F88966', 1, 'Ziehmon','2023-08-14 23:26:34'),
('3100F8F829', 1, 'micha','2023-08-14 22:55:55');
UNLOCK TABLES;
