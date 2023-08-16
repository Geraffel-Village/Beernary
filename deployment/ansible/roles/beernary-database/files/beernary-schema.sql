--
-- Table structure for table `consume`
--

DROP TABLE IF EXISTS `consume`;
CREATE TABLE `consume` (
  `autoid` int(11) NOT NULL AUTO_INCREMENT,
  `id` varchar(10) NOT NULL,
  `pulses` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`autoid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
CREATE TABLE `event` (
  `eventid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `selected` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`eventid`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

--
-- Table structure for table `keg`
--

DROP TABLE IF EXISTS `keg`;
CREATE TABLE `keg` (
  `kegid` int(11) NOT NULL AUTO_INCREMENT,
  `eventid` int(11) NOT NULL,
  `volume` smallint(6) NOT NULL,
  `pulses` int(11) DEFAULT '0',
  `isempty` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`kegid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` varchar(10) NOT NULL,
  `tapid` varchar(10) NOT NULL,
  `name` varchar(50) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
