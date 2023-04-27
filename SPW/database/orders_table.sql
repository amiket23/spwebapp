USE [users_db]
GO

/****** Object:  Table [dbo].[orders]    Script Date: 27-04-2023 01:01:52 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[orders](
	[order_id] [int] IDENTITY(1,1) NOT NULL,
	[product] [varchar](255) NOT NULL,
	[name] [varchar](255) NOT NULL,
	[username] [varchar](255) NOT NULL,
	[email] [varchar](255) NOT NULL,
	[price] [varchar](255) NOT NULL,
	[quantity] [varchar](255) NOT NULL,
	[total] [varchar](255) NOT NULL,
	[Address] [varchar](255) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[order_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

