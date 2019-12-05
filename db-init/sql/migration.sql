-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema #MYSQL_DB#
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema #MYSQL_DB#
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `#MYSQL_DB#` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `#MYSQL_DB#` ;

-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`ecotypes`
-- -----------------------------------------------------
CREATE TABLE `#MYSQL_DB#`.`ecotypes` (
	  `id` SMALLINT(5) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(191) NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE);
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`contigs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`contigs` (
	  `id` SMALLINT(8) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(191) NOT NULL,
	  `ecotype_id` SMALLINT(8) UNSIGNED NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`stations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`stations` (
	  `id` SMALLINT(8) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(12) NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`gene_reads`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`gene_reads` (
	  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `contig_id` SMALLINT(8) UNSIGNED NOT NULL,
	  `gene_id` MEDIUMINT(8) UNSIGNED NOT NULL,
	  `station_id` SMALLINT(8) UNSIGNED NOT NULL,
	  `read_number` INT(10) UNSIGNED NOT NULL,
	  `read_length` INT(10) UNSIGNED NOT NULL,
	  `gc_content` DECIMAL(4,2) UNSIGNED NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `gene_read_station_unique` (`gene_id` ASC, `read_number` ASC, `station_id` ASC) VISIBLE,
	  INDEX `station_fk_idx` (`station_id` ASC) VISIBLE,
	  INDEX `contig_fk_idx` (`contig_id` ASC) VISIBLE,
	  CONSTRAINT `contig_fk`
	    FOREIGN KEY (`gene_reads_contigs`)
	    REFERENCES `#MYSQL_DB#`.`contigs` (`id`),
	  CONSTRAINT `station_fk`
	    FOREIGN KEY (`gene_reads_stations`)
	    REFERENCES `#MYSQL_DB#`.`stations` (`id`),
	  CONSTRAINT `genes_fk`
	    FOREIGN KEY (`gene_reads_genes`)
	    REFERENCES `#MYSQL_DB#`.`genes` (`gene_id`)
        )
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`gene_reads`
-- -----------------------------------------------------
CREATE TABLE `genes` (
	  `gene_id` MEDIUMINT unsigned NOT NULL AUTO_INCREMENT,
	  `length` SMALLINT(8) unsigned NOT NULL,
	  `ecotype_id` SMALLINT(8) unsigned NOT NULL,
	  PRIMARY KEY (`gene_id`),
	  UNIQUE KEY `gene_id_UNIQUE` (`gene_id`),
	  CONSTRAINT `ecotype_fk`
	    FOREIGN KEY (`genes_ecotypes`)
	    REFERENCES `#MYSQL_DB#`.`ecotypes` (`id`)
	)
	ENGINE = InnoDB
	DEFAULT CHAR SET = utf8mb4
	COLLATE=utf8mb4_0900_ai_ci;

-- -----------------------------------------------------

	SET SQL_MODE=@OLD_SQL_MODE;
	SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
	SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
