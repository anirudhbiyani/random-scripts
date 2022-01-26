Import-Module AzureAD

### These are variable you need to update to reflect your environment
$Admin = ""
$AdminPassword = ""
$Directory = ""
$NewUserPassword = ""

### Create a PowerShell connection to my directory. If you do not want to specify the password in the script, you can simply replace this with "Connect-AzureAD", which will prompt for a username and password.
### $SecPass = ConvertTo-SecureString $AdminPassword -AsPlainText -Force
### $Cred = New-Object System.Management.Automation.PSCredential ($Admin, $SecPass)
### Connect-AzureAD -Credential $Cred
# Connect-AzureAD
Connect-MsolService

### Create a new Password Profile for the new users. We'll be using the same password for all new users in this example
$PasswordProfile = New-Object -TypeName Microsoft.Open.AzureAD.Model.PasswordProfile
$PasswordProfile.Password = $NewUserPassword

### Import the csv file. You will need to specify the path and file name of the CSV file in this cmdlet
$NewUsers = import-csv -Path "C:\Users\aniruddhab\Desktop\SEC_Users.csv"

### Loop through all new users in the file. We'll use the ForEach cmdlet for this.
Foreach ($NewUser in $NewUsers)
{
### Construct the UserPrincipalName, the MailNickName and the DisplayName from the input data in the file
    $UPN = $NewUser.firstname + "." + $NewUser.lastname + "@" + $Directory
    $DisplayName = $NewUser.firstname + " " + $NewUser.lastname + " (" + $NewUser.Department + ")"
    $MailNickName = $NewUser.firstname + "." + $NewUser.lastname
    $Address = $NewUser.street + "." + $NewUser.city + "." + $NewUser.province

### Now that we have all the necessary data for to create the new user, we can execute the New-AzureADUser cmdlet
  # New-AzureADUser -UserPrincipalName $UPN -AccountEnabled $false -DisplayName $DisplayName -GivenName $NewUser.firstname -MailNickName $MailNickName -Surname $NewUser.lastname -Department $NewUser.department -JobTitle $NewUser.title -PasswordProfile $PasswordProfile -City $NewUser.city -Country $NewUser.country -Mobile $NewUser.mobile -State $NewUser.state -StreetAddress $Address -UserType Member -PostalCode $NewUser.zipcode
  # New-MsolUser -UserPrincipalName $UPN -City $NewUser.city -State $NewUser.State -Country $NewUser.Country -DisplayName $NewUser.DisplayName
    New-MsolUser -UserPrincipalName $UPN -City $NewUser.city -State $NewUser.state -Country $NewUser.Country -DisplayName $DisplayName -Department $NewUser.department -FirstName $NewUser.firstname -LastName $NewUser.lastname -MobilePhone $NewUser.phone -Title $NewUser.title -UserType Member
}
