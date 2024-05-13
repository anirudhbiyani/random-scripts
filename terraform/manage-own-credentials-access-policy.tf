data "aws_iam_policy_document" "manage-own-credentials-access-policy-document" {
  provider = "aws.charlie16"
  statement {
    sid = "AllowViewAccountInfo"

    actions = [
  "iam:GetAccountPasswordPolicy",
  "iam:GetAccountSummary",
  "iam:ListUsers",
  "iam:ListVirtualMFADevices",
]

    resources = [
      "*",
    ]
  }

  statement {
    sid = "AllowManageOwnPasswords"
     actions = [
   "iam:ChangePassword",
   "iam:GetUser",
 ]

     resources = [
       "arn:aws:iam::${var.aws_account_number}:user/&{aws:username}",
     ]
   }
 
    statement {
    sid = "AllowManageOwnAccessKeys"

    actions = [
                "iam:CreateAccessKey",
                "iam:DeleteAccessKey",
                "iam:ListAccessKeys",
                "iam:UpdateAccessKey",
    ]

    resources = [
      "arn:aws:iam::${var.aws_account_number}:user/&{aws:username}",
    ]

  }


  statement {
    sid = "AllowManageOwnSigningCertificates"

    actions = [
                "iam:DeleteSigningCertificate",
                "iam:ListSigningCertificates",
                "iam:UpdateSigningCertificate",
                "iam:UploadSigningCertificate",
            ]

    resources = [
      "arn:aws:iam::${var.aws_account_number}:user/&{aws:username}",
    ]
  }


  statement {
    sid = "AllowManageOwnSSHPublicKeys"

    actions = [
                "iam:DeleteSSHPublicKey",
                "iam:GetSSHPublicKey",
                "iam:ListSSHPublicKeys",
                "iam:UpdateSSHPublicKey",
                "iam:UploadSSHPublicKey",
            ]

    resources = [
      "arn:aws:iam::${var.aws_account_number}:user/&{aws:username}",
    ]
  }


 statement {
    sid = "AllowManageOwnGitCredentials"

    actions = [
                "iam:CreateServiceSpecificCredential",
                "iam:DeleteServiceSpecificCredential",
                "iam:ListServiceSpecificCredentials",
                "iam:ResetServiceSpecificCredential",
                "iam:UpdateServiceSpecificCredential",
            ]

    resources = [
      "arn:aws:iam::${var.aws_account_number}:user/&{aws:username}",
    ]
  }


 statement {
    sid = "AllowManageOwnVirtualMFADevice"

    actions = [
                "iam:CreateVirtualMFADevice",
                "iam:DeleteVirtualMFADevice",
            ]

    resources = [
      "arn:aws:iam::${var.aws_account_number}:mfa/&{aws:username}",
    ]
  }


 statement {
    sid = "AllowManageOwnUserMFA"

    actions = [
                "iam:EnableMFADevice",
                "iam:ListMFADevices",
                "iam:ResyncMFADevice",
            ]

    resources = [
      "arn:aws:iam::${var.aws_account_number}:user/&{aws:username}",
    ]
  }

  statement {
          sid = "DeactivateMFADevice"
          actions = ["iam:DeactivateMFADevice"]
          resources = ["arn:aws:iam::${var.aws_account_number}:user/&{aws:username}"]
          condition = {
                          test = "BoolIfExists"
                          variable = "aws:MultiFactorAuthPresent"
                          values = [ "true", ]
                      }
            }
}
resource "aws_iam_policy" "manage-own-credentials-access-policy" {
 provider = "aws.charlie16"
 name = "manage-own-credentials-access-policy"
 policy = "${data.aws_iam_policy_document.manage-own-credentials-access-policy-document.json}"
}
