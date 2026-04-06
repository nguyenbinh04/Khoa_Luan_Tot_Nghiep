-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th4 06, 2026 lúc 05:02 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `hethonggiaothong_kltn`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `cameras`
--

CREATE TABLE `cameras` (
  `Id` int(11) NOT NULL,
  `TenCamera` varchar(255) NOT NULL,
  `LoaiNguon` varchar(50) NOT NULL,
  `DuongDan` varchar(500) NOT NULL,
  `TrangThai` bit(1) DEFAULT b'1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `cameras`
--

INSERT INTO `cameras` (`Id`, `TenCamera`, `LoaiNguon`, `DuongDan`, `TrangThai`) VALUES
(1, 'Camera Ngã Tư Test', 'Video', 'lane.mp4', b'1');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `cauhinhvung`
--

CREATE TABLE `cauhinhvung` (
  `Id` int(11) NOT NULL,
  `CameraId` int(11) NOT NULL,
  `LoaiVung` varchar(50) NOT NULL,
  `ToaDoJson` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `cauhinhvung`
--

INSERT INTO `cauhinhvung` (`Id`, `CameraId`, `LoaiVung`, `ToaDoJson`) VALUES
(23, 1, 'Lan_XeMay', '[{\"x\":681,\"y\":365},{\"x\":737,\"y\":353},{\"x\":893,\"y\":596},{\"x\":743,\"y\":613}]'),
(24, 1, 'Vach_DenDo', '[{\"x\":681,\"y\":365},{\"x\":737,\"y\":353},{\"x\":893,\"y\":596},{\"x\":743,\"y\":613}]');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `lichsuvipham`
--

CREATE TABLE `lichsuvipham` (
  `Id` int(11) NOT NULL,
  `CameraId` int(11) NOT NULL,
  `BienSo` varchar(50) DEFAULT 'Khong xac dinh',
  `LoaiViPham` varchar(100) NOT NULL,
  `ThoiGian` datetime NOT NULL,
  `DuongDanAnh` varchar(500) NOT NULL,
  `TrangThaiXuLy` varchar(50) DEFAULT 'Chờ duyệt',
  `DuongDanAnhBienSo` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `lichsuvipham`
--

INSERT INTO `lichsuvipham` (`Id`, `CameraId`, `BienSo`, `LoaiViPham`, `ThoiGian`, `DuongDanAnh`, `TrangThaiXuLy`, `DuongDanAnhBienSo`) VALUES
(123, 1, 'ID 3', 'Vuot Den Do', '2026-04-06 18:41:28', '20260406_184128_vp_id3.jpg', 'Chờ duyệt', NULL),
(124, 1, 'ID 87', 'Vuot Den Do', '2026-04-06 18:41:47', '20260406_184147_vp_id87.jpg', 'Chờ duyệt', NULL),
(125, 1, 'ID 361', 'Vuot Den Do', '2026-04-06 18:42:58', '20260406_184258_vp_id361.jpg', 'Chờ duyệt', NULL),
(126, 1, 'ID 449', 'Vuot Den Do', '2026-04-06 18:43:10', '20260406_184310_vp_id449.jpg', 'Chờ duyệt', NULL),
(127, 1, 'ID 3', 'Vuot Den Do', '2026-04-06 18:56:03', '20260406_185603_vp_3.jpg', 'Chờ duyệt', NULL),
(128, 1, 'ID 7', 'Vuot Den Do', '2026-04-06 18:56:10', '20260406_185610_vp_7.jpg', 'Chờ duyệt', NULL),
(129, 1, 'ID -1', 'Vuot Den Do', '2026-04-06 18:56:12', '20260406_185612_vp_-1.jpg', 'Chờ duyệt', NULL),
(130, 1, 'ID 29', 'Vuot Den Do', '2026-04-06 18:56:39', '20260406_185639_vp_29.jpg', 'Chờ duyệt', NULL),
(131, 1, 'ID 26', 'Vuot Den Do', '2026-04-06 18:56:42', '20260406_185642_vp_26.jpg', 'Chờ duyệt', NULL),
(132, 1, 'Xe 14', 'Vuot Den Do', '2026-04-06 19:12:42', '20260406_191242_id_14.jpg', 'Chờ duyệt', NULL),
(133, 1, 'Xe 81', 'Vuot Den Do', '2026-04-06 19:13:18', '20260406_191318_id_81.jpg', 'Chờ duyệt', NULL),
(134, 1, 'Xe 101', 'Vuot Den Do', '2026-04-06 19:13:27', '20260406_191327_id_101.jpg', 'Chờ duyệt', NULL),
(135, 1, 'Xe 3', 'Vuot Den Do', '2026-04-06 19:14:51', '20260406_191451_id_3.jpg', 'Chờ duyệt', NULL),
(136, 1, 'Xe 7', 'Vuot Den Do', '2026-04-06 19:14:59', '20260406_191459_id_7.jpg', 'Chờ duyệt', NULL),
(137, 1, 'Xe 19', 'Vuot Den Do', '2026-04-06 19:15:17', '20260406_191517_id_19.jpg', 'Chờ duyệt', NULL),
(138, 1, 'Xe 46', 'Vuot Den Do', '2026-04-06 19:15:36', '20260406_191536_id_46.jpg', 'Chờ duyệt', NULL),
(139, 1, 'Xe 83', 'Vuot Den Do', '2026-04-06 19:15:53', '20260406_191553_id_83.jpg', 'Chờ duyệt', NULL),
(140, 1, 'Xe 105', 'Vuot Den Do', '2026-04-06 19:16:01', '20260406_191601_id_105.jpg', 'Chờ duyệt', NULL),
(141, 1, 'Xe 133', 'Vuot Den Do', '2026-04-06 19:16:10', '20260406_191610_id_133.jpg', 'Chờ duyệt', NULL),
(142, 1, 'Xe 150', 'Vuot Den Do', '2026-04-06 19:16:13', '20260406_191613_id_150.jpg', 'Chờ duyệt', NULL),
(143, 1, 'Xe 161', 'Vuot Den Do', '2026-04-06 19:16:19', '20260406_191619_id_161.jpg', 'Chờ duyệt', NULL),
(144, 1, 'Xe 169', 'Vuot Den Do', '2026-04-06 19:16:23', '20260406_191623_id_169.jpg', 'Chờ duyệt', NULL),
(145, 1, 'Xe 181', 'Vuot Den Do', '2026-04-06 19:16:34', '20260406_191634_id_181.jpg', 'Chờ duyệt', NULL),
(146, 1, 'Xe 207', 'Vuot Den Do', '2026-04-06 19:16:51', '20260406_191651_id_207.jpg', 'Chờ duyệt', NULL),
(147, 1, 'Xe 281', 'Vuot Den Do', '2026-04-06 19:17:22', '20260406_191722_id_281.jpg', 'Chờ duyệt', NULL),
(148, 1, 'Xe 299', 'Vuot Den Do', '2026-04-06 19:17:33', '20260406_191733_id_299.jpg', 'Chờ duyệt', NULL),
(149, 1, 'Xe 352', 'Vuot Den Do', '2026-04-06 19:18:38', '20260406_191838_id_352.jpg', 'Chờ duyệt', NULL),
(150, 1, 'Xe 392', 'Vuot Den Do', '2026-04-06 19:19:54', '20260406_191954_id_392.jpg', 'Chờ duyệt', NULL),
(151, 1, 'Xe 398', 'Vuot Den Do', '2026-04-06 19:20:03', '20260406_192003_id_398.jpg', 'Chờ duyệt', NULL),
(152, 1, 'Xe 400', 'Vuot Den Do', '2026-04-06 19:20:04', '20260406_192004_id_400.jpg', 'Chờ duyệt', NULL),
(153, 1, 'Xe 415', 'Vuot Den Do', '2026-04-06 19:20:31', '20260406_192031_id_415.jpg', 'Chờ duyệt', NULL),
(154, 1, 'Xe 426', 'Vuot Den Do', '2026-04-06 19:20:38', '20260406_192038_id_426.jpg', 'Chờ duyệt', NULL),
(155, 1, 'Xe 429', 'Vuot Den Do', '2026-04-06 19:20:42', '20260406_192042_id_429.jpg', 'Chờ duyệt', NULL),
(156, 1, 'Xe 6', 'Vuot Den Do', '2026-04-06 19:48:51', '20260406_194851_id_6.jpg', 'Chờ duyệt', NULL),
(157, 1, 'Xe 18', 'Vuot Den Do', '2026-04-06 19:49:08', '20260406_194908_id_18.jpg', 'Chờ duyệt', NULL),
(158, 1, 'Xe 48', 'Vuot Den Do', '2026-04-06 19:49:32', '20260406_194932_id_48.jpg', 'Chờ duyệt', NULL),
(159, 1, 'Xe 59', 'Vuot Den Do', '2026-04-06 19:49:34', '20260406_194934_id_59.jpg', 'Chờ duyệt', NULL),
(160, 1, 'Xe 87', 'Vuot Den Do', '2026-04-06 19:49:52', '20260406_194952_id_87.jpg', 'Chờ duyệt', NULL),
(161, 1, 'Xe 101', 'Vuot Den Do', '2026-04-06 19:49:53', '20260406_194953_id_101.jpg', 'Chờ duyệt', NULL),
(162, 1, 'Xe 112', 'Vuot Den Do', '2026-04-06 19:50:01', '20260406_195001_id_112.jpg', 'Chờ duyệt', NULL),
(163, 1, 'Xe 178', 'Vuot Den Do', '2026-04-06 19:50:36', '20260406_195036_id_178.jpg', 'Chờ duyệt', NULL),
(164, 1, 'Xe 190', 'Vuot Den Do', '2026-04-06 19:50:39', '20260406_195039_id_190.jpg', 'Chờ duyệt', NULL),
(165, 1, 'Xe 204', 'Vuot Den Do', '2026-04-06 19:50:53', '20260406_195053_id_204.jpg', 'Chờ duyệt', NULL),
(166, 1, 'Xe 284', 'Vuot Den Do', '2026-04-06 19:51:25', '20260406_195125_id_284.jpg', 'Chờ duyệt', NULL),
(167, 1, 'Xe 289', 'Vuot Den Do', '2026-04-06 19:51:27', '20260406_195127_id_289.jpg', 'Chờ duyệt', NULL),
(168, 1, 'Xe 298', 'Vuot Den Do', '2026-04-06 19:51:38', '20260406_195138_id_298.jpg', 'Chờ duyệt', NULL),
(169, 1, 'Xe 31', 'Vuot Den Do', '2026-04-06 19:53:34', '20260406_195334_id_31.jpg', 'Chờ duyệt', NULL),
(170, 1, 'Xe 32', 'Vuot Den Do', '2026-04-06 19:53:35', '20260406_195335_id_32.jpg', 'Chờ duyệt', NULL),
(171, 1, 'Xe 6', 'Vuot Den Do', '2026-04-06 19:57:09', '20260406_195709_id_6.jpg', 'Chờ duyệt', NULL),
(172, 1, 'Xe 19', 'Vuot Den Do', '2026-04-06 19:57:37', '20260406_195737_id_19.jpg', 'Chờ duyệt', NULL),
(173, 1, 'Xe 24', 'Vuot Den Do', '2026-04-06 19:57:44', '20260406_195744_id_24.jpg', 'Chờ duyệt', NULL),
(174, 1, 'Xe 25', 'Vuot Den Do', '2026-04-06 19:57:50', '20260406_195750_id_25.jpg', 'Chờ duyệt', NULL),
(175, 1, 'Xe ID 3', 'Vuot Den Do', '2026-04-06 20:08:59', '2eaeca02-591b-4fba-9eae-54c182c8b355.jpg', 'Chờ duyệt', ''),
(176, 1, 'Xe ID 16', 'Vuot Den Do', '2026-04-06 20:09:15', '2560e620-8293-414c-abad-a2ba5a12f136.jpg', 'Chờ duyệt', 'f6f2d3ba-3d20-4b95-a755-cb51a4718eba.jpg'),
(177, 1, 'Xe ID 22', 'Vuot Den Do', '2026-04-06 20:09:19', 'a97af63a-6f21-48a0-be99-f89b968ca84c.jpg', 'Chờ duyệt', ''),
(178, 1, 'Xe ID 3', 'Vuot Den Do', '2026-04-06 20:13:05', '54ccdaee-ffff-4257-8116-1245fdacfeff.jpg', 'Chờ duyệt', ''),
(179, 1, 'Xe ID 22', 'Vuot Den Do', '2026-04-06 20:13:21', '8a34a63d-f8d3-430b-8acf-2eba6ddd7169.jpg', 'Chờ duyệt', ''),
(180, 1, 'Xe ID 25', 'Vuot Den Do', '2026-04-06 20:13:23', '87e88c1a-b344-4c14-9378-74a711a6f649.jpg', 'Chờ duyệt', ''),
(181, 1, 'Xe ID 55', 'Vuot Den Do', '2026-04-06 20:13:42', 'c4a9bdce-0831-4dff-b89f-6b752869f562.jpg', 'Chờ duyệt', ''),
(182, 1, 'Xe ID 89', 'Vuot Den Do', '2026-04-06 20:14:01', '814048cd-3a80-4c69-ba70-5144fa506435.jpg', 'Chờ duyệt', ''),
(183, 1, 'Xe ID 110', 'Vuot Den Do', '2026-04-06 20:14:09', 'a5fe426c-1709-48d0-a275-1dc349cdb2ca.jpg', 'Chờ duyệt', ''),
(184, 1, 'Xe ID 5', 'Vuot Den Do', '2026-04-06 20:24:03', '26af91ec-bef2-46c6-b340-be03a77d3470.jpg', 'Chờ duyệt', ''),
(185, 1, 'Xe ID 1', 'Vuot Den Do', '2026-04-06 20:24:04', 'ec0c6e2a-ed33-40c6-8274-1368458c6ddd.jpg', 'Chờ duyệt', ''),
(186, 1, 'Xe ID 12', 'Vuot Den Do', '2026-04-06 20:24:08', '34f98af0-86d5-4669-82aa-9719df56ef22.jpg', 'Chờ duyệt', ''),
(187, 1, 'Xe ID 49', 'Vuot Den Do', '2026-04-06 20:24:21', '5698dba1-a104-4ba2-b6a0-9e537fc4a5d9.jpg', 'Chờ duyệt', ''),
(188, 1, 'Xe ID 70', 'Vuot Den Do', '2026-04-06 20:24:33', 'c3301c12-0081-4242-8d71-9919f8d6571f.jpg', 'Chờ duyệt', ''),
(189, 1, 'Xe ID 81', 'Vuot Den Do', '2026-04-06 20:24:38', '5b5d85fa-5734-42de-8f22-4df83c084edd.jpg', 'Chờ duyệt', ''),
(190, 1, 'Xe ID 90', 'Vuot Den Do', '2026-04-06 20:24:49', '86ff81b9-0679-44ce-a13d-a8081eaf2e45.jpg', 'Chờ duyệt', ''),
(191, 1, 'Xe ID 106', 'Vuot Den Do', '2026-04-06 20:24:57', '57e9ba15-2231-4dc2-93d5-421c56222ba3.jpg', 'Chờ duyệt', ''),
(192, 1, 'Xe ID 108', 'Vuot Den Do', '2026-04-06 20:25:00', '96b22551-89cf-40d3-b3ad-ec5220b2f748.jpg', 'Chờ duyệt', ''),
(193, 1, 'Xe ID 113', 'Vuot Den Do', '2026-04-06 20:25:00', '370a2af0-c7bd-4d3d-8a9a-0a6a4efbd4a4.jpg', 'Chờ duyệt', ''),
(194, 1, 'Xe ID 7', 'Vuot Den Do', '2026-04-06 20:25:51', '5d8ef98c-9b7f-4a44-a57e-a571a87f4193.jpg', 'Chờ duyệt', ''),
(195, 1, 'Xe ID 8', 'Vuot Den Do', '2026-04-06 20:25:52', '7df27f8e-d7cf-451b-9947-d79995a9069c.jpg', 'Chờ duyệt', ''),
(196, 1, 'Xe ID 19', 'Vuot Den Do', '2026-04-06 20:26:08', '7b569d93-ac63-4dbf-b248-9b3b6eae86a0.jpg', 'Chờ duyệt', ''),
(197, 1, 'Xe ID 3', 'Vuot Den Do', '2026-04-06 20:30:24', '2ceed5a7-6db8-4a24-a7d6-2d14ba74caac.jpg', 'Chờ duyệt', ''),
(198, 1, 'Xe ID 9', 'Vuot Den Do', '2026-04-06 20:30:25', '0369cc86-89ae-4b5e-8cda-9e22fe703a8d.jpg', 'Chờ duyệt', ''),
(199, 1, 'Xe ID 19', 'Vuot Den Do', '2026-04-06 20:30:41', '5d6ca292-e44f-4e13-bfe6-2094d76eb16b.jpg', 'Chờ duyệt', ''),
(200, 1, 'Xe ID 27', 'Vuot Den Do', '2026-04-06 20:30:43', 'be67ee8f-b1f4-48d0-b616-197faa83de02.jpg', 'Chờ duyệt', ''),
(201, 1, 'Xe ID 52', 'Vuot Den Do', '2026-04-06 20:31:01', 'a9acbab0-ccec-42ac-adf8-1d6cdefa9ffc.jpg', 'Chờ duyệt', ''),
(202, 1, 'Xe ID 5', 'Vuot Den Do', '2026-04-06 20:36:04', 'a6e3f6b6-7c06-443c-8775-7c45e96b5e1e.jpg', 'Chờ duyệt', '33695e90-9b2b-4143-a02f-84ac95e57461.jpg'),
(203, 1, 'Xe ID 16', 'Vuot Den Do', '2026-04-06 20:36:23', '50af0eb1-698f-4489-9102-80a5203076aa.jpg', 'Chờ duyệt', 'c43f9363-df58-432b-b018-c060cf21aaa5.jpg'),
(204, 1, 'Xe ID 17', 'Vuot Den Do', '2026-04-06 20:36:23', '2fc575a3-0105-4e42-b845-623f6bdc7d77.jpg', 'Chờ duyệt', '09cb8733-0e68-4f59-adb0-a2001ef3bcbc.jpg'),
(205, 1, 'Xe ID 18', 'Vuot Den Do', '2026-04-06 20:36:24', 'f148021f-b605-4633-bcbc-ecacb17d144e.jpg', 'Chờ duyệt', '162ef766-4bf9-4fba-b3e7-c78cb1593925.jpg'),
(206, 1, 'Xe ID 27', 'Vuot Den Do', '2026-04-06 20:36:27', 'b007d663-055c-4486-9a54-3d6b6b6077ac.jpg', 'Chờ duyệt', ''),
(207, 1, 'Xe ID 46', 'Vuot Den Do', '2026-04-06 20:36:35', 'c4fff3c6-a5b2-47c2-858e-814be1dc15e5.jpg', 'Chờ duyệt', ''),
(208, 1, 'Xe ID 58', 'Vuot Den Do', '2026-04-06 20:36:48', 'e6540789-3607-471e-9909-ae3b8a395e08.jpg', 'Chờ duyệt', 'cc08c70e-d222-4c30-8453-71bdbbd913a0.jpg'),
(209, 1, 'Xe ID 60', 'Vuot Den Do', '2026-04-06 20:36:49', '370013c3-403a-4d5f-92db-551f1b193177.jpg', 'Chờ duyệt', 'dfd5a67a-2ce4-43c8-828c-4dcf88137ee4.jpg'),
(210, 1, 'Xe ID 66', 'Vuot Den Do', '2026-04-06 20:36:54', 'd9012bab-9603-48e7-819a-e0d604e4d34f.jpg', 'Chờ duyệt', '4dac70c1-9f60-4da0-a9c2-510d8321b05b.jpg'),
(211, 1, 'Xe ID 85', 'Vuot Den Do', '2026-04-06 20:37:00', 'b4a5f66f-2bf9-4fa9-abbf-05ace55c7f58.jpg', 'Chờ duyệt', ''),
(212, 1, 'Xe ID 93', 'Vuot Den Do', '2026-04-06 20:37:02', '1ffe9f4f-99f7-4b1d-b3f3-d8dccc1927b5.jpg', 'Chờ duyệt', ''),
(213, 1, 'Xe ID 109', 'Vuot Den Do', '2026-04-06 20:37:05', 'e5548f81-35db-43ce-82a3-d8fb8b2a7c67.jpg', 'Chờ duyệt', ''),
(214, 1, 'Xe ID 126', 'Vuot Den Do', '2026-04-06 20:37:10', '38186b87-c451-4cb2-a9b8-2709c2d1fc7e.jpg', 'Chờ duyệt', '82a96789-0a43-4968-b289-83c1e0319074.jpg'),
(215, 1, 'Xe ID 114', 'Vuot Den Do', '2026-04-06 20:37:10', '71a82567-743c-4918-82ac-a10274ef6509.jpg', 'Chờ duyệt', 'ae565a8a-e0da-455c-bc46-bb1623e785b1.jpg'),
(216, 1, 'Xe ID 130', 'Vuot Den Do', '2026-04-06 20:37:11', 'fb1d3160-a770-442f-b006-f58f89515231.jpg', 'Chờ duyệt', ''),
(217, 1, 'Xe ID 150', 'Vuot Den Do', '2026-04-06 20:37:18', '4cbce6c1-51f4-4397-b18a-805c91e158f1.jpg', 'Chờ duyệt', ''),
(218, 1, 'Xe ID 161', 'Vuot Den Do', '2026-04-06 20:37:20', '401ff30f-ad7e-4ff5-b46a-736927971948.jpg', 'Chờ duyệt', ''),
(219, 1, 'Xe ID 173', 'Vuot Den Do', '2026-04-06 20:37:24', '881c6434-7800-45ce-9ea3-ba42c323220e.jpg', 'Chờ duyệt', ''),
(220, 1, 'Xe ID 180', 'Vuot Den Do', '2026-04-06 20:37:27', '1daa0ac5-de2b-4f97-84a8-9ad384d323d2.jpg', 'Chờ duyệt', ''),
(221, 1, 'Xe ID 188', 'Vuot Den Do', '2026-04-06 20:37:29', 'cdf5c298-6fe4-4cd6-82b1-a0ab855227c9.jpg', 'Chờ duyệt', 'e33c25b6-f916-40c0-964f-7dc5c3c72f91.jpg'),
(222, 1, 'Xe ID 201', 'Vuot Den Do', '2026-04-06 20:37:34', '9a1b1b2a-f151-4f64-8ef4-65fbc7ed699c.jpg', 'Chờ duyệt', ''),
(223, 1, 'Xe ID 207', 'Vuot Den Do', '2026-04-06 20:37:36', '9635d83e-af8b-4656-8a05-2d3ee0328f80.jpg', 'Chờ duyệt', ''),
(224, 1, 'Xe ID 229', 'Vuot Den Do', '2026-04-06 20:37:42', 'fdb88b03-9e74-4b60-a3d5-eb0d9fb6707c.jpg', 'Chờ duyệt', 'b2ab5073-e4b8-4491-920b-e033bc03af29.jpg'),
(225, 1, 'Xe ID 234', 'Vuot Den Do', '2026-04-06 20:37:43', '077238ff-7a8b-425e-b18e-c6e7206be46e.jpg', 'Chờ duyệt', ''),
(226, 1, 'Xe ID 252', 'Vuot Den Do', '2026-04-06 20:37:52', '7894e647-f3a2-4d79-861a-f2fe46b426c9.jpg', 'Chờ duyệt', ''),
(227, 1, 'Xe ID 275', 'Vuot Den Do', '2026-04-06 20:37:59', 'c37d53a3-3145-468b-8ea5-e6dec01f123b.jpg', 'Chờ duyệt', ''),
(228, 1, 'Xe ID 283', 'Vuot Den Do', '2026-04-06 20:38:09', '0b3cc990-c7d2-4456-89aa-40bb9abb3aea.jpg', 'Chờ duyệt', 'b6628491-ec07-4ca8-a6d0-7ab5d8270226.jpg'),
(229, 1, 'Xe ID 293', 'Vuot Den Do', '2026-04-06 20:38:12', 'd1b45b39-4e41-4aac-b9c1-e5ca979f95af.jpg', 'Chờ duyệt', ''),
(230, 1, 'Xe ID 303', 'Vuot Den Do', '2026-04-06 20:38:16', 'b012f997-ebfd-4d40-9d0f-dbbc005dc793.jpg', 'Chờ duyệt', ''),
(231, 1, 'Xe ID 322', 'Vuot Den Do', '2026-04-06 20:38:25', '5a473c13-d657-4072-8fe1-bc712304b2ec.jpg', 'Chờ duyệt', ''),
(232, 1, 'Xe ID 353', 'Vuot Den Do', '2026-04-06 20:38:33', 'e35e052c-4930-45fb-9000-fa9e09e4d8f3.jpg', 'Chờ duyệt', ''),
(233, 1, 'Xe ID 374', 'Vuot Den Do', '2026-04-06 20:38:43', 'd08ba906-0608-4e03-b55f-bd95641fde01.jpg', 'Chờ duyệt', 'ff53933a-e599-41fb-9408-ccd2a7b4999e.jpg'),
(234, 1, 'Xe ID 13', 'Vuot Den Do', '2026-04-06 20:46:26', 'ccbbc0f2-9817-4ff7-aec3-6ba8a27c5188.jpg', 'Chờ duyệt', ''),
(235, 1, 'Xe ID 17', 'Vuot Den Do', '2026-04-06 20:46:37', '796748af-3f6b-4236-a859-091ef653f166.jpg', 'Chờ duyệt', ''),
(236, 1, 'Xe ID 54', 'Vuot Den Do', '2026-04-06 20:47:11', 'fb7b7546-ef5d-41ea-b45f-73671f090e23.jpg', 'Chờ duyệt', ''),
(237, 1, 'Xe ID 59', 'Vuot Den Do', '2026-04-06 20:47:13', 'cd1554d4-5c09-438f-85bc-1456a48ce970.jpg', 'Chờ duyệt', ''),
(238, 1, 'Xe ID 73', 'Vuot Den Do', '2026-04-06 20:47:15', '805f344d-67b1-4d3f-bfdb-90627f0736c5.jpg', 'Chờ duyệt', ''),
(239, 1, 'Xe ID 80', 'Vuot Den Do', '2026-04-06 20:47:17', '1ab09e0f-be46-447e-9aa8-fd9ca0833134.jpg', 'Chờ duyệt', ''),
(240, 1, 'Xe ID 89', 'Vuot Den Do', '2026-04-06 20:47:22', '55d2c22b-b28a-4063-a473-f3b4c3d6e069.jpg', 'Chờ duyệt', ''),
(241, 1, 'Xe ID 90', 'Vuot Den Do', '2026-04-06 20:47:25', 'b127c316-e33a-42ce-a6aa-9e418e89cb84.jpg', 'Chờ duyệt', 'f1a12770-4f8a-44ed-b013-c18a7f964c10.jpg'),
(242, 1, 'Xe ID 110', 'Vuot Den Do', '2026-04-06 20:47:37', '4a7ecc82-d28d-4a01-af50-9d4d12957941.jpg', 'Chờ duyệt', 'f045ab3e-e46e-45b2-9241-6be14f756471.jpg'),
(243, 1, 'Xe ID 129', 'Vuot Den Do', '2026-04-06 20:47:43', 'a1e3f33f-7e1c-4357-b6ff-e4883e8071e2.jpg', 'Chờ duyệt', ''),
(244, 1, 'Xe ID 148', 'Vuot Den Do', '2026-04-06 20:48:01', '52a996a0-8031-4397-87eb-d9ee5f11f2a6.jpg', 'Chờ duyệt', '03d2b739-f4d7-4e3e-8585-96fec28e71b5.jpg');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `cameras`
--
ALTER TABLE `cameras`
  ADD PRIMARY KEY (`Id`);

--
-- Chỉ mục cho bảng `cauhinhvung`
--
ALTER TABLE `cauhinhvung`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `CameraId` (`CameraId`);

--
-- Chỉ mục cho bảng `lichsuvipham`
--
ALTER TABLE `lichsuvipham`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `CameraId` (`CameraId`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `cameras`
--
ALTER TABLE `cameras`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT cho bảng `cauhinhvung`
--
ALTER TABLE `cauhinhvung`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT cho bảng `lichsuvipham`
--
ALTER TABLE `lichsuvipham`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=245;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `cauhinhvung`
--
ALTER TABLE `cauhinhvung`
  ADD CONSTRAINT `cauhinhvung_ibfk_1` FOREIGN KEY (`CameraId`) REFERENCES `cameras` (`Id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `lichsuvipham`
--
ALTER TABLE `lichsuvipham`
  ADD CONSTRAINT `lichsuvipham_ibfk_1` FOREIGN KEY (`CameraId`) REFERENCES `cameras` (`Id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
