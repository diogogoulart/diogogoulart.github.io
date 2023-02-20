CREATE schema IF NOT EXISTS estetica;

USE estetica;

CREATE TABLE IF NOT EXISTS `employee` (
  `EMPLOYEE_ID` INTEGER NOT NULL AUTO_INCREMENT,
  `NAME` varchar(50) DEFAULT NULL,
  `DATE_OF_BIRTH` date NOT NULL,
  `EMAIL` varchar(50) NOT NULL,
  `PHONE_NUMBER` varchar(20) NOT NULL,
  `ADDRESS` varchar(120) NOT NULL,
  `HIRE_DATE` date NOT NULL,
  `SALARY` decimal(8,2) NOT NULL,
  `IBAN` char(34) NOT NULL,
  PRIMARY KEY (`EMPLOYEE_ID`)
) ;

CREATE TABLE IF NOT EXISTS `client` (
`CLIENT_ID` INTEGER NOT NULL AUTO_INCREMENT,
`NAME` varchar(50) DEFAULT NULL,
`DATE_OF_BIRTH` date DEFAULT NULL,
`PHONE_NUMBER` varchar(20) DEFAULT NULL,
`TAX_IDENTIFICATION_NUMBER` char(9) DEFAULT NULL, -- nr de contribuinte pt tem 9 digitos, deve ser int ou char?
`PROFESSION` varchar(50) DEFAULT NULL,
`NATIONALITY` varchar(2) DEFAULT NULL,
`ADDRESS` varchar(120) NULL,
`FEMALE` tinyint(1) default 0, 
`CARDIAC_PROBLEMS` tinyint(1) DEFAULT 0,
`PREGNANCY` tinyint(1) DEFAULT 0,
`ONCOLOGIC_PROBLEMS` tinyint(1) DEFAULT 0,
`DIABETES` tinyint(1) DEFAULT 0,
`PACEMAKER'S` tinyint(1) DEFAULT 0,
`METAL_PROSTHESIS` tinyint(1) DEFAULT 0,
`OTHER_MEDICATION` tinyint(1) DEFAULT 0,
`DERMATOLOGIC_PROBLEMS` tinyint(1) DEFAULT 0,
`ANY_PEELING?` tinyint(1) DEFAULT 0,
`OBSERVATIONS` varchar(100) DEFAULT NULL, 
PRIMARY KEY (`CLIENT_ID`)
);

CREATE TABLE IF NOT EXISTS `country` (
  `COUNTRY_ID` varchar(2) NOT NULL,
  `COUNTRY_NAME` varchar(40) DEFAULT NULL,
  `REGION_ID`TINYINT DEFAULT NULL,
  PRIMARY KEY (`COUNTRY_ID`)
);

CREATE TABLE IF NOT EXISTS `region` (
  `REGION_ID` TINYINT NOT NULL,
  `REGION_NAME` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`REGION_ID`)
) ;

CREATE TABLE IF NOT EXISTS `room` (
`ROOM_ID` INTEGER NOT NULL AUTO_INCREMENT,
`CAPACITY` INTEGER NOT NULL,
`AREA` INTEGER NOT NULL,
PRIMARY KEY (`ROOM_ID`)
);

CREATE TABLE IF NOT EXISTS `service` (
`SERVICE_ID` INTEGER NOT NULL AUTO_INCREMENT,
`NAME` varchar(50) NOT NULL,
`PRICE` decimal(5,2) NOT NULL,
`TASK` varchar(50) DEFAULT NULL,
`DURATION` time NOT NULL,
`CATEGORY` varchar(30) NOT NULL,
CHECK (`CATEGORY` in ('Foto Depilação', 'Epilação', 'Rosto', 'Serviços Mãos', 'Serviços Pés',
'Foto Rejuvenescimento Unissexo','Micropigmentação','Pestanas', 'Massagem','Cavitação','Radiofrequência',
'Eletroestimulação','Pressoterapia')),
PRIMARY KEY (`SERVICE_ID`)
);

CREATE TABLE IF NOT EXISTS `appointment` (
  `APT_ID` INTEGER NOT NULL AUTO_INCREMENT,
  `CLIENT_ID` INTEGER DEFAULT NULL,
  `APT_NAME` varchar(50) default NULL,
  `DATE` Date NOT NULL,
  `TIME` Time NOT NULL,
  `APT_PRICE` decimal(8,2) DEFAULT 0, #not null?? idk
  `APT_DURATION` time DEFAULT NULL,
  `STATUS` VARCHAR(10) DEFAULT 'Booked',
  CHECK (`STATUS` in ('Booked','Cancel','Concluded')),
  PRIMARY KEY (`APT_ID`)
);

CREATE TABLE IF NOT EXISTS `appointment_service` (
`APT_SER_ID` INTEGER NOT NULL AUTO_INCREMENT,
`APT_ID` INTEGER NOT NULL,
`SERVICE_ID` INTEGER NOT NULL,
`EMPLOYEE_ID` INTEGER NOT NULL,
`ROOM_ID` INTEGER NOT NULL,
PRIMARY KEY (`APT_SER_ID`)
);

CREATE TABLE IF NOT EXISTS `supplier` (
`SUPPLIER_ID` INTEGER NOT NULL AUTO_INCREMENT,
`NAME` varchar(20) NOT NULL,
`PHONE_NUMBER` varchar(20) DEFAULT NULL,
`EMAIL` varchar(50) DEFAULT NULL,
PRIMARY KEY (`SUPPLIER_ID`)
);

CREATE TABLE IF NOT EXISTS `product` (
`PRODUCT_ID` INTEGER NOT NULL AUTO_INCREMENT,
`NAME` varchar(50) NOT NULL,
`PRICE` decimal(7,2) DEFAULT NULL, -- price for selling
`OBS` varchar(100) DEFAULT NULL, -- brief explanation of what it does
`QNT_IN_STOCK` INTEGER NOT NULL,
`IN_HOUSE_USE` TINYINT NOT NULL,
`SUPPLIER_ID` INTEGER DEFAULT NULL,
PRIMARY KEY (`PRODUCT_ID`)
);

CREATE TABLE IF NOT EXISTS `product_service`(
`SERVICE_ID` INTEGER NOT NULL,
`PRODUCT_ID` INTEGER NOT NULL
);

CREATE INDEX index_ProdServ ON `product_service` (`SERVICE_ID`, `PRODUCT_ID`);

CREATE TABLE IF NOT EXISTS `stock_request` (
`REQUEST_ID` INTEGER NOT NULL AUTO_INCREMENT,
`PRODUCT_ID` INTEGER NOT NULL,
`QUANTITY` INTEGER NOT NULL,
PRIMARY KEY (`REQUEST_ID`)
);


CREATE TABLE IF NOT EXISTS `rating` (
`RATING_ID` INTEGER NOT NULL AUTO_INCREMENT,
`APT_SER_ID` INTEGER NOT NULL,
`DATE` date NOT NULL,
`RATING` integer NOT NULL,
CHECK (`RATING` in (1,2,3,4,5)),
PRIMARY KEY (`RATING_ID`)
);

CREATE TABLE IF NOT EXISTS `service_historical`(
`HISTORICAL_ID` INTEGER NOT NULL AUTO_INCREMENT,
`APT_SER_ID` INTEGER NOT NULL,
`LAZER_POWER` INTEGER DEFAULT NULL,
`BELLY_SIZE` DECIMAL (5,2) DEFAULT NULL,
`ARM_SIZE` DECIMAL (5,2) DEFAULT NULL,
`LEG_SIZE` DECIMAL (5,2) DEFAULT NULL,
PRIMARY KEY (`HISTORICAL_ID`)
); 

#Table log
CREATE TABLE IF NOT EXISTS `log` (
LOG_ID INTEGER UNSIGNED AUTO_INCREMENT PRIMARY KEY,
DT DATETIME NOT NULL,
USR VARCHAR(63),
EV VARCHAR(15),
MSG VARCHAR(255)
);

ALTER TABLE `client`
ADD CONSTRAINT FK_Client_Country
FOREIGN KEY (`NATIONALITY`) REFERENCES `estetica`.`country`(`COUNTRY_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `country`
ADD CONSTRAINT FK_country_region
FOREIGN KEY (`REGION_ID`) REFERENCES `estetica`.`region` (`REGION_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `appointment`
ADD CONSTRAINT FK_AptClient
FOREIGN KEY (`CLIENT_ID`) REFERENCES `estetica`.`client`(`CLIENT_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `service_historical`
ADD CONSTRAINT FK_ServHist_Apt_Serv
FOREIGN KEY (`APT_SER_ID`) REFERENCES `estetica`.`appointment_service`(`APT_SER_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `rating`
ADD CONSTRAINT FK_Rating_AptServ
FOREIGN KEY (`APT_SER_ID`) REFERENCES `estetica`.`appointment_service`(`APT_SER_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `appointment_service`
ADD CONSTRAINT FK_AptServ_Apt
FOREIGN KEY (`APT_ID`) REFERENCES `estetica`.`appointment`(`APT_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE,
ADD CONSTRAINT FK_AptServ_Serv
FOREIGN KEY (`SERVICE_ID`) REFERENCES `estetica`.`service`(`SERVICE_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE,
ADD CONSTRAINT FK_AptServ_Employee
FOREIGN KEY (`EMPLOYEE_ID`) REFERENCES `estetica`.`employee`(`EMPLOYEE_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE,
ADD CONSTRAINT FK_AptServ_Room
FOREIGN KEY (`ROOM_ID`) REFERENCES `estetica`.`room`(`ROOM_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `product`
ADD CONSTRAINT FK_Prod_Supp
FOREIGN KEY (`SUPPLIER_ID`) REFERENCES `estetica`.`supplier`(`SUPPLIER_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `stock_request`
ADD CONSTRAINT FK_ReqProd_Prod
FOREIGN KEY (`PRODUCT_ID`) REFERENCES `estetica`.`product`(`PRODUCT_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE `product_service`
ADD CONSTRAINT ProdServ_Service
FOREIGN KEY (`SERVICE_ID`) REFERENCES `estetica`.`service`(`SERVICE_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE,
ADD CONSTRAINT FK_ProdServ_Prod
FOREIGN KEY (`PRODUCT_ID`) REFERENCES `estetica`.`product`(`PRODUCT_ID`)
ON DELETE RESTRICT ON UPDATE CASCADE;

#Trigger 1
#Update the appointment price whenever a service is added to the apointment
DELIMITER //
CREATE TRIGGER upd_apt_price
AFTER INSERT 
ON `appointment_service`
FOR EACH ROW
BEGIN
		UPDATE appointment SET apt_price = apt_price + (SELECT s.price
														FROM service s
                                                        WHERE s.service_id= new.service_id)
		WHERE apt_id= new.apt_id;
END//

#Trigger 2
DELIMITER $$
CREATE TRIGGER insert_apt_log
AFTER INSERT
ON appointment
FOR EACH ROW
BEGIN
INSERT log (DT,USR,EV,MSG) 
VALUES (NOW(),USER(),"add",CONCAT(NEW.date,' ',NEW.time));
END $$
DELIMITER ;

#Trigger 3
DELIMITER $$
CREATE TRIGGER update_apt_log
AFTER UPDATE
ON appointment
FOR EACH ROW
BEGIN
INSERT log (DT,USR,EV,MSG) VALUES
(NOW(),USER(),"update",CONCAT(NEW.date,' ',NEW.time));
END $$
DELIMITER ;

#Trigger 4
DELIMITER $$
CREATE TRIGGER delete_apt_log
BEFORE DELETE
ON appointment
FOR EACH ROW
BEGIN
INSERT log (DT,USR,EV,MSG) VALUES
(NOW(),USER(),"delete",CONCAT(OLD.date,' ',OLD.time));
END $$
DELIMITER ;

#G
#Invoice part 1
CREATE OR REPLACE VIEW invoice_header AS
SELECT a.apt_id as InvoiceNumber, a.date as DateOfIssue,  c.name as ClientName, 
c.tax_identification_number as NIF, c.address as BillingAddress,
(a.apt_price - (a.apt_price*0.23)) as SubTotal, '23%' as Tax, a.apt_price as Total 
FROM appointment a, client c
WHERE a.client_id=c.client_id;


CREATE OR REPLACE VIEW invoice_details AS
SELECT a.apt_id as InvoiceNumber, s.name as Service, s.price as ServicePrice
FROM client c, appointment a, appointment_service aps, service s
WHERE a.client_id=c.client_id AND a.apt_id=aps.apt_id AND aps.service_id=s.service_id;


INSERT INTO `region` (`REGION_ID`, `REGION_NAME`) VALUES
(1, 'Europe'),
(2, 'Americas'),
(3, 'Asia'),
(4, 'Middle East and Africa');

INSERT INTO `country` (`COUNTRY_ID`, `COUNTRY_NAME`, `REGION_ID`) VALUES
('AR', 'Argentina', 2),
('AU', 'Australia', 3),
('BE', 'Belgium', 1),
('BR', 'Brazil', 2),
('CA', 'Canada', 2),
('CH', 'Switzerland', 1),
('CN', 'China', 3),
('DE', 'Germany', 1),
('DK', 'Denmark', 1),
('EG', 'Egypt', 4),
('ES', 'Spain', 1),
('FR', 'France', 1),
('HK', 'HongKong', 3),
('IL', 'Israel', 4),
('IN', 'India', 3),
('IT', 'Italy', 1),
('JP', 'Japan', 3),
('KW', 'Kuwait', 4),
('MX', 'Mexico', 2),
('NG', 'Nigeria', 4),
('NL', 'Netherlands', 1),
('PT', 'Portugal', 1),
('SG', 'Singapore', 3),
('UK', 'United Kingdom', 1),
('US', 'United States of America', 2),
('ZM', 'Zambia', 4),
('ZW', 'Zimbabwe', 4);

INSERT INTO employee (EMPLOYEE_ID,NAME,DATE_OF_BIRTH,EMAIL,PHONE_NUMBER,ADDRESS,HIRE_DATE,SALARY,IBAN) VALUES
( 1 ,'Sílvia Rocha Santos','2002-12-20' , 'SilviaSantos@estetica.com' , 939386107 , 'Travessa Moura Sá, Coimbra, 3020-136 Coimbra' , '2021-02-14', 900 , 'PT50306662662792882689160554030983' ),
( 2 , 'Bárbara Oliveira Costa Luz', '1980-05-06' , 'BarbaraLuz@estetica.com' , 937480328 , 'Rua Augusta, Cernache, Coimbra,3040-757 Coimbra' , '2019-07-23' , 900 , 'PT50827117973737459120849051253078' ),
( 3 , 'Isabella Coelho Peixoto', '1991-03-04' , 'IsabellaPeixoto@estetica.com' , 916319689 , 'R Doutor Paulo Quintela, São Martinho De Árvore, Coimbra, 3025-487 Coimbra' , '2021-04-25' , 900 , 'PT50309476589802711676154892198022' )
;

INSERT INTO `client` VALUES
(1,'João Felipe Rezende','1979-06-04',914082036,821390174,'Telemarketer','PT','Rua do Pinhal 23, Figueira da Foz',0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL),
(2,'Mariana Sales','1977-12-06',911418356,445655763,'Architect','PT','Rua Gil Eanes 19, Coimbra',1,0, 0, 0, 0, 0, 0, 0, 0, 0, NULL),
(3,'Milena Cardoso','1986-07-09',915844966,601765161,'Secretary','BR','Ladeira da Santiva 213, Coimbra', 1 ,0, 0, 0, 0, 0, 0, 0, 0, 0, NULL),
(4,'Clara Aragão','1988-07-17',934928402,99994045,'Educator', 'PT','Rua Manuel Rodrigues da Maia 276, Tocha',1, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL),
(5,'Ana Júlia Correia','1963-02-17',936937275,973539113,'Respiratory Therapist', 'BR', 'Rua das Canas 22, Figueira da Foz',1, 0, 1, 0, 0, 0, 0, 0, 0, 0, NULL),
(6, 'Arthur Gomes', '1962-10-05', 934092637, 258022439, 'Firefighter', 'FR','Rue Eugène Lumeau 10, Paris', 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, NULL),
(7, 'Renan Cavalcanti', '1962-04-18', 917217440, 146005006, 'Therapist', 'ES', 'C. la Pentenera 9, Sevilha', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL),
(8,'Clarice Barbosa', '1982-05-04', 968485903, 10074838, 'Urban Planner','PT','Travessa Estevão Pinto 1, Lisboa',1,0, 0, 0, 0, 0, 0, 0, 0, 0, NULL),
(9,'Ana Laura Pereira', '1962-12-05', 968154681, 36298525, 'Computer Systems Analyst','PT','Rua da Guiné 13, Figueira da Foz', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL),
(10, 'Luigi Gomes' , '1979-07-09' , 939313597, 539622106, 'Patrol Officer', 'IT', 'Rua Celulose Billerud 19, Figueira da Foz', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, NULL)
;

INSERT INTO `room` VALUES
(1,10,40),
(2,2,12),
(3,2,12),
(4,3,16)
;

INSERT INTO `supplier` VALUES
(1,'Sunshine Beautytian', 238340462, 'SunshineBeautytian@sunshinebeautytian.com'),
(2, 'Beauty Swan', 232713645, 'BeautySwan@beautyswan.com'),
(3, 'Allure Oryx', 298485476, 'AllureOryx@allureoryx.com'),
(4, 'NuView Beauty Supply', 212968723, 'NuViewBeautySupply@nuviewbeautysupply.com'),
(5, 'The Skin Treatments', 214570641, 'TheSkinTreatments@theskintreatments.com')
;

INSERT INTO `service` VALUES
( 1 , 'Manicure Completa' , 7 , NULL , '00:20' , 'Serviços Mãos' ),
( 2 , 'Remoção de Verniz Gel com Manicure' , 8 , 'Remover o verniz gel com a lima' , '00:40' , 'Serviços Mãos' ),
( 3 , 'Verniz Gel' , 11 , 'Manutenção de verniz gel' , '00:45' , 'Serviços Mãos' ),
( 4 , 'Reforço de Gel com Tips' , 37 , NULL ,'01:30' , 'Serviços Mãos' ),
( 5 , 'Reforço de Gel com Moldes' , 27 , NULL , '01:30' , 'Serviços Mãos' ),
( 6 , 'Reforço de Gel sobre Unhas Naturais' , 21 , NULL , '01:00' , 'Serviços Mãos' ),
( 7 , 'Manutenção de Unhas de Gel' , 14 , NULL , '01:00' , 'Serviços Mãos' ),
( 8 , 'Aplicação de brilhantes, autocolantes e desenhos' , 2 , '5 min cada unidade' , '00:05' , 'Serviços Mãos' ),
( 9 , 'Sobrancelhas a Cera' , 3.5 , NULL , '00:10' , 'Epilação' ),
( 10 , 'Sobrancelhas a Pinça' , 3.5 , NULL , '00:10' , 'Epilação' ),
( 11 , 'Sobrancelhas a Linha' , 8 , NULL , '00:15' , 'Epilação' ),
( 12 , 'Design de Sobrancelhas ' , 11 , NULL , '00:30' , 'Epilação' ),
( 13 , 'Buço' , 3.5 , NULL , '00:10' , 'Epilação' ),
( 14 , 'Contorno de Rosto' , 5 , NULL , '00:10' , 'Epilação' ),
( 15 , 'Axilas' , 5 , NULL , '00:10' , 'Epilação' ),
( 16 , 'Braços' , 9 , NULL , '00:20' , 'Epilação' ),
( 17 , 'Virilha pouco Cavada' , 6 , NULL , '00:15' , 'Epilação' ),
( 18 , 'Virilha Cavada ' , 8 , NULL , '00:20' , 'Epilação' ),
( 19 , 'Virilha Total' , 10 , NULL , '00:20' , 'Epilação' ),
( 20 , 'Costas' , 12 , NULL , '00:20' , 'Epilação' ),
( 21 , 'Meia Perna' , 7 , NULL , '00:15' , 'Epilação' ),
( 22 , 'Perna Inteira' , 12 , NULL , '00:30' , 'Rosto' ),
( 23 , 'Limpeza de Pele' , 45 , NULL , '01:30' , 'Rosto' ),
( 24 , 'Tratamento de Pele' , 50 , NULL , '01:00' , 'Rosto' ),
( 25 , 'Minifacial' , 25 , NULL , '01:00' , 'Rosto' ),
( 26 , 'Aplicação de ampola' , 10 , NULL , '00:10' , 'Rosto' ),
( 27 , 'Peelings químicos' , 60 , NULL , '01:00' , 'Rosto' ),
( 28 , 'Mesoterapia' , 90 , NULL , '01:00' , 'Rosto' ),
( 29 , 'Aplicação de Toxina botulínica (Botox)' , 110 , NULL , '01:00' , 'Rosto' ),
( 30 , 'Ácido Hialurónico' , 45 , NULL , '01:00' , 'Rosto' ),
( 31 , 'Maquilhagem' , 50 , NULL , '00:45' , 'Rosto' ),
( 32 , 'Arranjar Unhas dos Pés' , 7 , NULL , '00:30' , 'Serviços Pés' ),
( 33 , 'Remoção de Verniz Gel Unhas Pés' , 8 , NULL , '00:10' , 'Serviços Pés' ),
( 34 , 'Pedicure Completa sem Aplicação de Cor' , 13.5 , NULL , '00:40' , 'Serviços Pés' ),
( 35 , 'Pedicure Completa com Aplicação de Verniz Normal' , 15 , NULL , '00:45' , 'Serviços Pés' ),
( 36 , 'Pedicure Completa com Aplicação de Verniz Gel' , 18 , NULL , '00:45' , 'Serviços Pés' ),
( 37 , '1º Vez Lábios ou Sobrancelhas ' , 100 , NULL , '02:00' , 'Micropigmentação' ),
( 38 , 'Retoque Lábios ou Sobrancelhas' , 60 , NULL , '01:30' , 'Micropigmentação' ),
( 39 , 'Lifting de Pestanas com Coloração' , 25 , NULL , '01:00' , 'Pestanas' ),
( 40 , '1º Vez Extansão de Pestanas' , 40 , NULL , 150 , 'Pestanas' ),
( 41 , 'Manutenção da Extensão de Pestanas ' , 25 , NULL , '01:30' , 'Pestanas' ),
( 42 , 'Radiofrequência Zona à Escolha ' , 40 , NULL , '00:30' , 'Radiofrequência' ),
( 43 , 'Foto Rejuvenescimento Rosto' , 40 , NULL , '01:00' , 'Foto Rejuvenescimento Unissexo' ),
( 44 , 'Foto Rejuvenescimento Colo' , 45 , NULL , '01:00' , 'Foto Rejuvenescimento Unissexo' ),
( 45 , 'Foto Rejuvenescimento Mãos' , 30 , NULL , '00:30' , 'Foto Rejuvenescimento Unissexo' ),
( 46 , 'Cavitação Zona à Escolha' , 40 , NULL , '00:30' , 'Cavitação' ),
( 47 , 'Eletroestimulação Zona à Escolha' , 15 , NULL , '00:20' , 'Eletroestimulação' ),
( 48 , 'Massagem sessão 45min' , 30 , NULL , '00:45' , 'Massagem' ),
( 49 , 'Massagem sessão 90 min' , 50 , NULL , '01:30' , 'Massagem' ),
( 50 , 'Pressoterapia (sessão)' , 10 , NULL , '00:45' , 'Pressoterapia' ),
( 51 , 'Foto Depilação Buço' , 13 , NULL , '00:10' , 'Foto Depilação' ),
( 52 , ' Foto Depilação Entre Sobrancelhas' , 10 , NULL , '00:5' , 'Foto Depilação' ),
( 53 , 'Foto Depilação Maças do Rosto' , 20 , NULL , '00:10' , 'Foto Depilação' ),
( 54 , 'Foto Depilação Patilhas' , 14 , NULL , '00:10' , 'Foto Depilação' ),
( 55 , 'Foto Depilação Face Lateral' , 25 , NULL , '00:15' , 'Foto Depilação' ),
( 56 , 'Foto Depilação Queixo' , 20 , NULL , '00:10' , 'Foto Depilação' ),
( 57 , 'Foto Depilação Buço+Queixo' , 30 , NULL , '00:20' , 'Foto Depilação' ),
( 58 , 'Foto Depilação Rosto Total' , 40 , NULL , '00:30' , 'Foto Depilação' ),
( 59 , 'Foto Depilação Colo' , 25 , NULL , '00:20' , 'Foto Depilação' ),
( 60 , 'Foto Depilação Axilas' , 25 , NULL , '00:10' , 'Foto Depilação' ),
( 61 , 'Foto Depilação Mamilos' , 14 , NULL , '00:05' , 'Foto Depilação' ),
( 62 , 'Foto Depilação Umbigo ' , 10 , NULL , '00:05' , 'Foto Depilação' ),
( 63 , 'Foto Depilação Linha Alba' , 13 , NULL , '00:10' , 'Foto Depilação' ),
( 64 , ' Foto Depilação Zona Lombar' , 30 , NULL , '00:15' , 'Foto Depilação' ),
( 65 , 'Foto Depilação Braços' , 50 , NULL , '00:20' , 'Foto Depilação' ),
( 66 , 'Foto Depilação Mãos' , 20 , NULL , '00:10' , 'Foto Depilação' ),
( 67 , 'Foto Depilação Pés' , 20 , NULL , '00:10' , 'Foto Depilação' ),
( 68 , 'Foto Depilação Glúteos' , 40 , NULL , '00:25' , 'Foto Depilação' ),
( 69 , 'Foto Depilação Meia Perna' , 60 , NULL , '00:15' , 'Foto Depilação' ),
( 70 , 'Foto Depilação Perna Completa' , 100 , NULL , '00:30' , 'Foto Depilação' ),
( 71 , 'Foto Depilação Virilha Cavada ' , 25 , NULL , '00:15' , 'Foto Depilação' ),
( 72 , 'Foto Depilação Virilha Total' , 40 , NULL , '00:20' , 'Foto Depilação' ),
( 73 , 'Foto Depilação Entre Sobrancelhas Homem' , 12 , NULL , '00:05' , 'Foto Depilação' ),
( 74 , 'Foto Depilação Maças do Rosto Homem' , 22 , NULL , '00:10' , 'Foto Depilação' ),
( 75 , 'Foto Depilação Patilhas Homem' , 16 , NULL , '00:10' , 'Foto Depilação' ),
( 76 , 'Foto Depilação Orelhas Homem' , 15 , NULL , '00:15' , 'Foto Depilação' ),
( 77 , 'Foto Depilação Narinas Homem' , 10 , NULL , '00:15' , 'Foto Depilação' ),
( 78 , 'Foto Depilação Bigode Homem' , 15 , NULL , '00:15' , 'Foto Depilação' ),
( 79 , 'Foto Depilação Pescoço Homem' , 15 , NULL , '00:20' , 'Foto Depilação' ),
( 80 , 'Foto Depilação Barba Completa Homem' , 45 , NULL , '00:25' , 'Foto Depilação' ),
( 81 , 'Foto Depilação Rosto Total Homem' , 50 , NULL , '00:30' , 'Foto Depilação' ),
( 82 , 'Foto Depilação Axilas Homem' , 30 , NULL , '00:10' , 'Foto Depilação' ),
( 83 , 'Foto Depilação Ombros Homem' , 40 , NULL , '00:15' , 'Foto Depilação' ),
( 84 , 'Foto Depilação Lombar Homem' , 40 , NULL , '00:15' , 'Foto Depilação' ),
( 85 , 'Foto Depilação Dorsal Homem' , 30 , NULL , '00:20' , 'Foto Depilação' ),
( 86 , 'Foto Depilação Costas Completas Homem' , 80 , NULL , '00:30' , 'Foto Depilação' ),
( 87 , 'Foto Depilação Toráx Homem' , 40 , NULL , '00:20' , 'Foto Depilação' ),
( 88 , 'Foto Depilação Abdómen Homem' , 40 , NULL , '00:30' , 'Foto Depilação' ),
( 89 , 'Foto Depilação Tórax+Abdomém Homem' , 70 , NULL , '00:30' , 'Foto Depilação' ),
( 90 , 'Foto Depilação Umbigo Homem' , 14 , NULL , '00:05' , 'Foto Depilação' ),
( 91 , 'Foto Depilação Linha Alba Homem' , 20 , NULL , '00:10' , 'Foto Depilação' ),
( 92 , 'Foto Depilação Braços Homem' , 60 , NULL , '00:30' , 'Foto Depilação' ),
( 93 , 'Foto Depilação Mãos Homem' , 25 , NULL , '00:10' , 'Foto Depilação' ),
( 94 , 'Foto Depilação Pés Homem' , 25 , NULL , '00:10' , 'Foto Depilação' ),
( 95 , 'Foto Depilação Meia Perna Homem' , 70 , NULL , '00:15' , 'Foto Depilação' ),
( 96 , 'Foto Depilação Perna Completa Homem' , 120 , NULL , '00:30' , 'Foto Depilação' ),
( 97 , 'Foto Depilação Virilha Homem' , 40 , NULL , '00:20' , 'Foto Depilação' ),
( 98 , 'Foto Depilação Glúteos Homem' , 50 , NULL , '00:20' , 'Foto Depilação');

INSERT INTO `product` VALUES
( 1 , 'Soft Cleanser' , 29.43 , NULL , 5 , 0 , 1 ),
( 2 , 'Deep Cleanser' , 36.86 , NULL , 2 , 0 , 2 ),
( 3 , 'Exfoliating Heating Paste' , 26.16 , NULL , 1 , 0 , 2 ),
( 4 , 'Skin Repair' , 47.93 , NULL , 2 , 0 , 2 ),
( 5 , 'Refresh Mask' , 42.23 , NULL , 6 , 0 , 2 ),
( 6 , 'Soft Cleanser Professional' , 29.0 , NULL , 6 , 1 , 1 ),
( 7 , 'Skin Repair Professional' , 128.0 , NULL , 1 , 1 , 4 ),
( 8 , 'Exfoliating Heating Paste Professional' , 32.4 , NULL , 6 , 1 , 1 ),
( 9 , 'Deep Cleasing Professional' , 37.0 , NULL , 4 , 1 , 5 ),
( 10 , 'Optimum Hydration' , 18.45 , NULL , 3 , 1 , 5 ),
( 11 , 'Ampoules Hyaluronic Acid' , 44.26 , NULL , 1 , 0 , 3 ),
( 12 , 'SunBlock UVP 50+' , 37.55 , NULL , 1 , 0 , 2 ),
( 13 , 'Tinted Day Cream 6 SPF' , 23.6 , NULL , 3 , 0 , 5 ),
( 14 , 'Body Scrub - Sugar Ritual' , 15.0 , NULL , 6 , 0 , 4 ),
( 15 , 'Even Tone Restructuring Serum' , 154.96 , NULL , 6 , 0 , 1 ),
( 16 , 'Ampoules Hyaluronic Acid Professional' , 26.68 , NULL , 6 , 1 , 4 ),
( 17 , 'Body Scrub - Sugar Ritual Profesional' , 29.7 , NULL , 3 , 1 , 5 ),
( 18 , 'Modeling Cream' , 24.69 , NULL , 2 , 1 , 1 ),
( 19 , 'White Tea Mask' , 25.51 , NULL , 4 , 1 , 1 ),
( 20 , 'Lipsomes Eye Lift' , 18.6 , NULL , 5 , 1 , 4 );

INSERT INTO appointment (APT_ID, CLIENT_ID, DATE, TIME) VALUES
( 1 , 1 , '2019-01-02' , '13:00' ),
( 2 , 2 , '2019-01-06' , '10:00' ),
( 3 , 2 , '2019-01-10' , '16:00' ),
( 4 , 6 , '2019-01-22' , '16:00' ),
( 5 , 4 , '2019-01-24' , '13:00' ),
( 6 , 2 , '2019-01-29' , '16:00' ),
( 7 , 6 , '2019-02-10' , '14:00' ),
( 8 , 7 , '2019-02-21' , '15:00' ),
( 9 , 6 , '2019-03-11' , '13:00' ),
( 10 , 4 , '2019-03-15' , '15:00' ),
( 11 , 7 , '2019-03-17' , '18:00' ),
( 12 , 1 , '2019-03-19' , '10:00' ),
( 13 , 6 , '2019-03-22' , '14:00' ),
( 14 , 8 , '2019-03-26' , '15:00' ),
( 15 , 3 , '2019-04-15' , '12:00' ),
( 16 , 6 , '2019-05-04' , '09:00' ),
( 17 , 4 , '2019-05-09' , '13:00' ),
( 18 , 9 , '2019-05-24' , '10:00' ),
( 19 , 6 , '2019-05-28' , '13:00' ),
( 20 , 6 , '2019-05-30' , '12:00' ),
( 21 , 4 , '2019-05-31' , '18:00' ),
( 22 , 1 , '2019-06-17' , '15:00' ),
( 23 , 5 , '2019-07-02' , '13:00' ),
( 24 , 4 , '2019-07-05' , '16:00' ),
( 25 , 2 , '2019-07-09' , '09:00' ),
( 26 , 8 , '2019-07-11' , '13:00' ),
( 27 , 7 , '2019-08-02' , '17:00' ),
( 28 , 6 , '2019-08-04' , '13:00' ),
( 29 , 7 , '2019-08-29' , '16:00' ),
( 30 , 6 , '2019-09-10' , '14:00' ),
( 31 , 3 , '2019-09-18' , '17:00' ),	
( 32 , 6 , '2019-09-20' , '14:00' ),
( 33 , 1 , '2019-09-20' , '14:00' ),
( 34 , 5 , '2019-09-28' , '17:00' ),
( 35 , 3 , '2019-09-30' , '17:00' ),
( 36 , 6 , '2019-10-04' , '09:00' ),
( 37 , 2 , '2019-10-05' , '15:00' ),
( 38 , 4 , '2019-10-25' , '12:00' ),
( 39 , 1 , '2019-10-26' , '10:00' ),
( 40 , 5 , '2019-11-01' , '09:00' ),
( 41 , 6 , '2019-11-07' , '14:00' ),
( 42 , 6 , '2019-11-14' , '17:00' ),
( 43 , 1 , '2019-12-19' , '18:00' ),
( 44 , 8 , '2019-12-28' , '17:00' ),
( 45 , 6 , '2019-12-31' , '12:00' ),
( 46 , 5 , '2020-01-18' , '12:00' ),
( 47 , 1 , '2020-02-10' , '11:00' ),
( 48 , 6 , '2020-02-19' , '18:00' ),
( 49 , 1 , '2020-02-29' , '17:00' ),
( 50 , 2 , '2020-03-10' , '14:00' ),
( 51 , 3 , '2020-03-18' , '17:00' ),
( 52 , 6 , '2020-04-07' , '15:00' ),
( 53 , 5 , '2020-04-14' , '17:00' ),
( 54 , 2 , '2020-04-15' , '18:00' ),
( 55 , 3 , '2020-04-30' , '15:00' ),
( 56 , 8 , '2020-05-04' , '13:00' ),
( 57 , 6 , '2020-05-08' , '09:00' ),
( 58 , 7 , '2020-05-29' , '15:00' ),
( 59 , 5 , '2020-06-06' , '10:00' ),
( 60 , 8 , '2020-06-17' , '16:00' ),
( 61 , 5 , '2020-06-30' , '13:00' ),
( 62 , 3 , '2020-07-27' , '10:00' ),
( 63 , 2 , '2020-08-01' , '15:00' ),
( 64 , 1 , '2020-08-04' , '17:00' ),
( 65 , 4 , '2020-08-21' , '16:00' ),
( 66 , 2 , '2020-09-02' , '13:00' ),
( 67 , 3 , '2020-09-02' , '14:00' ),
( 68 , 1 , '2020-09-05' , '17:00' ),
( 69 , 3 , '2020-09-09' , '18:00' ),
( 70 , 7 , '2020-09-11' , '13:00' ),
( 71 , 8 , '2020-09-14' , '12:00' ),
( 72 , 1 , '2020-09-17' , '18:00' ),
( 73 , 3 , '2020-09-19' , '17:00' ),
( 74 , 4 , '2020-09-26' , '14:00' ),
( 75 , 6 , '2020-10-08' , '16:00' ),
( 76 , 5 , '2020-10-15' , '12:00' ),
( 77 , 7 , '2020-10-17' , '11:00' ),
( 78 , 4 , '2020-10-17' , '14:00' ),
( 79 , 6 , '2020-10-21' , '14:00' ),
( 80 , 1 , '2020-11-12' , '14:00' ),
( 81 , 2 , '2020-11-18' , '16:00' ),
( 82 , 5 , '2020-11-21' , '12:00' ),
( 83 , 8 , '2020-11-22' , '11:00' ),
( 84 , 8 , '2020-11-24' , '13:00' ),
( 85 , 2 , '2020-11-28' , '14:00' ),
( 86 , 1 , '2020-12-05' , '17:00' ),
( 87 , 4 , '2020-12-08' , '13:00' ),
( 88 , 7 , '2020-12-12' , '12:00' ),
( 89 , 2 , '2020-12-12' , '10:00' ),
( 90 , 5 , '2020-12-17' , '16:00' ),
( 91 , 8 , '2020-12-20' , '13:00' ),
( 92 , 3 , '2020-12-22' , '16:00' ),
( 93 , 7 , '2021-01-18' , '11:00' ),
( 94 , 5 , '2021-01-18' , '15:00' ),
( 95 , 7 , '2021-02-09' , '10:00' ),
( 96 , 2 , '2021-02-17' , '12:00' ),
( 97 , 6 , '2021-02-20' , '14:00' ),
( 98 , 1 , '2021-03-01' , '09:00' ),
( 99 , 4 , '2021-04-05' , '13:00' ),
( 100 , 1 , '2021-04-12' , '17:00' ),	
( 101 , 4 , '2021-04-16' , '14:00' ),
( 102 , 3 , '2021-04-18' , '17:00' ),
( 103 , 6 , '2021-04-21' , '10:00' ),
( 104 , 5 , '2021-04-22' , '13:00' ),
( 105 , 3 , '2021-05-10' , '11:00' ),
( 106 , 8 , '2021-06-07' , '11:00' ),
( 107 , 5 , '2021-06-15' , '14:00' ),
( 108 , 8 , '2021-06-20' , '14:00' ),
( 109 , 7 , '2021-06-20' , '12:00' ),
( 110 , 6 , '2021-06-25' , '16:00' ),
( 111 , 3 , '2021-06-28' , '09:00' ),
( 112 , 5 , '2021-07-02' , '14:00' ),
( 113 , 7 , '2021-07-05' , '15:00' ),
( 114 , 7 , '2021-07-21' , '15:00' ),
( 115 , 2 , '2021-07-24' , '12:00' ),
( 116 , 3 , '2021-07-25' , '14:00' ),
( 117 , 4 , '2021-07-26' , '11:00' ),
( 118 , 3 , '2021-08-17' , '16:00' ),
( 119 , 8 , '2021-08-24' , '14:00' ),
( 120 , 1 , '2021-08-24' , '11:00' ),
( 121 , 8 , '2021-08-26' , '09:00' ),
( 122 , 1 , '2021-08-31' , '12:00' ),
( 123 , 8 , '2021-09-13' , '09:00' ),
( 124 , 3 , '2021-09-28' , '16:00' ),
( 125 , 10 , '2021-10-08' , '18:00' ),
( 126 , 8 , '2021-10-16' , '13:00' ),
( 127 , 5 , '2021-10-16' , '11:00' ),
( 128 , 3 , '2021-10-25' , '10:00' ),
( 129 , 6 , '2021-10-26' , '17:00' ),
( 130 , 1 , '2021-11-05' , '17:00' ),
( 131 , 8 , '2021-11-09' , '13:00' ),
( 132 , 6 , '2021-11-26' , '11:00' ),
( 133 , 7 , '2021-11-29' , '17:00' ),
( 134 , 5 , '2021-12-01' , '14:00' ),
( 135 , 5 , '2021-12-20' , '12:00' ),
( 136 , 5 , '2021-12-23' , '14:00' ),
( 137 , 1 , '2021-12-23' , '16:00' ),
( 138 , 5 , '2022-01-01' , '18:00' ),
( 139 , 4 , '2022-01-14' , '12:00' ),
( 140 , 8 , '2022-01-20' , '13:00' ),
( 141 , 1 , '2022-01-27' , '12:00' ),
( 142 , 2 , '2022-01-28' , '10:00' ),
( 143 , 6 , '2022-02-11' , '18:00' ),
( 144 , 8 , '2022-02-12' , '12:00' ),
( 145 , 1 , '2022-02-17' , '18:00' ),
( 146 , 7 , '2022-03-04' , '16:00' ),
( 147 , 5 , '2022-03-15' , '15:00' ),
( 148 , 5 , '2022-03-26' , '09:00' ),
( 149 , 5 , '2022-04-03' , '15:00' ),
( 150 , 2 , '2022-04-04' , '12:00' ),
( 151 , 4 , '2022-04-08' , '09:00' ),
( 152 , 9 , '2022-04-12' , '15:00' ),
( 153 , 6 , '2022-04-22' , '16:00' ),
( 154 , 7 , '2022-04-23' , '11:00' ),
( 155 , 5 , '2022-04-28' , '16:00' ),
( 156 , 4 , '2022-05-17' , '15:00' ),
( 157 , 3 , '2022-05-18' , '13:00' ),
( 158 , 1 , '2022-06-05' , '09:00' ),
( 159 , 3 , '2022-06-10' , '09:00' ),
( 160 , 6 , '2022-06-23' , '17:00' ),
( 161 , 6 , '2022-06-26' , '18:00' ),
( 162 , 7 , '2022-06-26' , '13:00' ),
( 163 , 7 , '2022-07-05' , '12:00' ),
( 164 , 5 , '2022-07-10' , '13:00' ),
( 165 , 5 , '2022-07-15' , '12:00' ),
( 166 , 2 , '2022-07-16' , '12:00' ),
( 167 , 10 , '2022-08-18' , '11:00' ),
( 168 , 6 , '2022-08-21' , '09:00' ),
( 169 , 1 , '2022-09-12' , '12:00' ),
( 170 , 2 , '2022-09-28' , '09:00' ),
( 171 , 8 , '2022-09-28' , '12:00' ),
( 172 , 6 , '2022-09-28' , '18:00' ),
( 173 , 3 , '2022-09-30' , '09:00' ),
( 174 , 7 , '2022-10-13' , '17:00' ),
( 175 , 6 , '2022-10-17' , '10:00' ),
( 176 , 8 , '2022-10-27' , '13:00' ),
( 177 , 1 , '2022-10-27' , '17:00' ),
( 178 , 1 , '2022-11-04' , '16:00' ),
( 179 , 3 , '2022-11-08' , '14:00' ),
( 180 , 2 , '2022-11-09' , '17:00' ),
( 181 , 3 , '2022-11-15' , '18:00' ),
( 182 , 7 , '2022-11-22' , '17:00' ),
( 183 , 5 , '2022-11-27' , '15:00' ),
( 184 , 1 , '2022-12-12' , '18:00' ),
( 185 , 10 , '2022-12-18' , '18:00' ),
( 186 , 2 , '2022-12-18' , '10:00' ),
( 187 , 3 , '2022-12-22' , '14:00' ),
( 188 , 9 , '2022-12-27' , '13:00' ),
( 189 , 10 , '2023-01-03' , '12:00' ),
( 190 , 7 , '2023-01-08' , '13:00' ),
( 191 , 3 , '2023-01-09' , '15:00' ),
( 192 , 8 , '2023-01-14' , '14:00' ),
( 193 , 6 , '2023-01-20' , '10:00' ),	
( 194 , 8 , '2023-01-27' , '12:00' ),
( 195 , 1 , '2023-01-31' , '18:00' ),
( 196 , 3 , '2023-02-05' , '15:00' ),
( 197 , 9 , '2023-02-07' , '17:00' ),
( 198 , 7 , '2023-02-10' , '18:00' ),
( 199 , 2 , '2023-02-12' , '09:00' );

INSERT INTO product_service VALUES
(39,20),
(23,9)
;

INSERT INTO stock_request VALUES
(1,2,4),
(2,12,2),
(3,18,2)
;

INSERT INTO appointment_service(APT_SER_ID, APT_ID, SERVICE_ID, EMPLOYEE_ID, ROOM_ID) VALUES
(1,143,54,2,1),
(2,54,35,2,1),
(3,191,80,3,3),
(4,125,91,1,3),
(5,135,64,2,3),
(6,62,4,3,2),
(7,9,87,2,2),
(8,115,37,2,2),
(9,17,82,3,2),
(10,162,56,2,3),
(11,180,86,1,2),
(12,136,87,3,2),
(13,197,42,2,1),
(14,151,62,1,1),
(15,67,83,1,2),
(16,184,71,2,2),
(17,45,26,2,2),
(18,175,14,2,2),
(19,86,19,3,1),
(20,13,66,2,3),
(21,5,92,1,2),
(22,84,17,3,2),
(23,169,62,1,2),
(24,195,22,3,2),
(25,21,34,2,2),
(26,124,70,2,1),
(27,151,58,2,2),
(28,197,54,3,3),
(29,49,91,3,1),
(30,139,86,2,1),
(31,5,1,1,2)
;

INSERT INTO service_historical(HISTORICAL_ID, APT_SER_ID, LAZER_POWER, BELLY_SIZE, ARM_SIZE, LEG_SIZE) VALUES
(1,28,87,NULL,NULL,NULL),
(2,12,NULL,31.60,264.85,35.88),
(3,15,NULL,36.15,154.71,48.41),
(4,16,88,NULL,NULL,NULL),
(5,17,134,NULL,NULL,NULL),
(6,19,NULL,15.94,113.73,29.30),
(7,22,NULL,21.79,NULL,20.23),
(8,10,122,NULL,NULL,NULL),
(9,27,NULL,37.91,285.10,68.59),
(10,1,NULL,52.71,182.21,32.82),
(11,14,68,NULL,NULL,NULL),
(12,20,NULL,71.93,353.93,103.48),
(13,13,NULL,NULL,259.12,145.66),
(14,15,111,NULL,NULL,NULL),
(15,16,NULL,28.55,109.81,59.51),
(16,29,NULL,24.80,252.34,77.09),
(17,21,50,NULL,NULL,NULL),
(18,24,NULL,93.74,279.14,193.29),
(19,5,NULL,38.69,260.86,109.60),
(20,28,93,NULL,NULL,NULL),
(21,27,121,NULL,NULL,NULL),
(22,1,152,NULL,NULL,NULL),
(23,27,NULL,66.79,384.03,110.83),
(24,18,124,NULL,NULL,NULL),
(25,5,137,NULL,NULL,NULL),
(26,19,NULL, 25.70, 143.83, 79.20),
(27,20,61,NULL,NULL,NULL),
(28,7, NULL, 27.38, 151.27, 67.82),
(29,15, NULL,44.12,360.88,246.71),
(30,22,45,NULL,NULL,NULL)
;

INSERT INTO rating (RATING_ID, APT_SER_ID, DATE, RATING) VALUES
(1, 2, '2020-04-16', 5),
(2, 5, '2021-11-05', 4),
(3, 9, '2019-05-09', 5),
(4, 12, '2021-12-23', 5),
(5, 17, '2019-12-31', 4),
(6, 21, '2019-01-24', 5),
(7, 22, '2020-11-25', 3),
(8, 26, '2021-09-28', 5),
(9, 27, '2022-04-09', 5),
(10, 29, '2020-02-29', 4),
(11, 30, '2022-01-15', 5)
;
