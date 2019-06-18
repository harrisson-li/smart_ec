USE [TestAutomation]
GO

/****** Object:  Table [dbo].[ec_phoenix_pack]    Script Date: 6/18/2019 2:33:17 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[ec_phoenix_pack](
	[__id__] [int] IDENTITY(1,1) NOT NULL,
	[env] [varchar](50) NOT NULL,
	[partner] [varchar](50) NOT NULL,
	[name] [varchar](100) NOT NULL,
	[data] [varchar](500) NULL,
	[salesforce_id] [varchar](100) NOT NULL,
	[package_id] [int] NOT NULL,
	[tags] [varchar](100) NULL,
PRIMARY KEY CLUSTERED
(
	[__id__] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

