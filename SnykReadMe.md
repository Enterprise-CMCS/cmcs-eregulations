# Snyk Scan

Snyk is a security tool that scans anything from repositories, CICD pipelines, Container Registries, IAC configs, and even the cloud environment. It checks for vulnerabilities within its implementation space and then is able to prioritize the most important, offer insight as to what is going on, and also provide a solution to fix the problem. It can be integrated as a workflow in the code to run and provide the findings, and there is also a dashboard that can be linked and can provide more functionality. Within the workflow, the entire repository is scanned based on the set trigger like a pull request, or a commit, or a time of day. The dashboard, on the other hand, can provide a centralized view of the issues and insights to improve security. It puts all the data into a nice GUI so that its easy to understand. Reports can be pulled for all resources current security status. The issues are all placed under one tab easily identifiable. There are also governance controls and policies that can be applied to the resources to enforce the security standards and best practices of the organization. And then as usual, there is also control on who has access to all this information and what they are able to do even if provided access.

## Setup Enterprise Snyk Organization

To setup Enterprise Snyk organization, please follow the instruction here: https://cloud.cms.gov/getting-started-snyk”.

## Logging In and Creating Snyk Token

Once the ticket is approved, navigate to this site to login using your EUA credentials: https://snyk.cms.gov/ . You may be asked to setup MFA upon login.

Once logged in, we need to setup the Snyk Token to authenticate from github. Go to the bottom left where your name is and click the arrow. Then go to "Account Settings" and under the "General" tab, there should be a section for "API Token". Click the generate button and save the token value to create a secret in the next step. 

Once the token is finished generating, navigate to git hub and find your repository. In the navigation tabs, click settings and then on the tab bar on the left, click Secrets and Variables under Security. Under that, click Actions. The secrets page should open and there might be secrets there for other services.

Click the big green "New Repository Secret" button. Then give your secret a unique name, like "Snyk_Token", and paste the copied token value under the box marked secret. Then click the "Add Secret" button. It should navigate back to the Secrets page and your secret should appear under "Repository Secrets". Now this token can be utilized in the workflow to authenticate with Snyk.

## Creating a Service Account and Providing the remaining arguments for the Jira Ticket Creation

Next, we need a service account to authenticate with Jira and create the tickets for the bugs Snyk found. 

Create JIRA Service account by following the instruction here: https://confluenceent.cms.gov/display/CAT/Requesting+a+Service+Account+for+JIRA

GitHub Service account by following the instruction here: https://confluenceent.cms.gov/pages/viewpage.action?spaceKey=MDSO&title=GitHub+Guide

Once the jira service account is created, you will be provided the Username and Password. Then login to jira with that account, go to the upper right where the account icon is and click it. Then click "Profile" and the profile page should load up. Then on the left, there is a navigation bar where you click "Personal Access Tokens". On the left side, there is a blue "Create token" button that you click. Then provide a unique token name and also decide if you want auto expiry or never expires. Then you can also choose how long before the token expires. Then click "create". Then a page loads with the secret value that you should copy and then hit next. Now you have the authentication token.

Go back to github and go to the secrets page and create secrets to store the Personal Access Token and Jira Host name. The PAT is the token just created in the last step, and the Host name is the first part of the jira url up to ".gov" without the "https://". For example, the homepage URL for eRegs Jira is "https://jiraent.cms.gov/projects/EREGCSC/summary". However, the host name is just "jiraent.cms.gov". Below is the variables and their descriptions:

```
    JIRA_TOKEN: This secret needs to hold the PAT value of the Jira Service Account.
    JIRA_HOST: The Jira Domain- EX. "jirarent.cms.gov".
```

# Current Implementation

The snyk-test.yml script is located in the .github/workflows. This document outlines the parts of the file that are modifiable and the controls that are located within. This document has 2 actions within. First is the regular snyk scan that runs on pull request, and the second is a cron job snyk scan and jira ticket creation. In the second action, the findings are posted to Jira as bugs in the backlog so that the team can just pull the ticket and fix the issue. The tickets can also be auto-assigned to a set team member who will fix it or is in charge of delegating the tasks.

## Pull Request or Cron Job

At the top, the document checks to see if a pull request was done on the main branch or if it’s the set time for the cron job. The branch can be changed to whichever branch needs testing however, the deployment will also have to be done to that branch. Also, pull_request can be changed to other triggers like push or schedule. The use for schedule is shown below. The cron job will run at midnight EST meaning that if you put ‘04***’, that is 4am in a different time zone but midnight here. If you want to modify the start time, this is what each position inside the quotes, '* * * * *', means. 'Minute Hour Date Month DayInWeek'. So its the minute in the hour, then the hour, then the date (1-30/31), then the month (1-12), then the day of the week (0-6). 

```
on:
  pull_request:
    branches: [ main ]
  schedule:
    - cron:  '0 4 * * *'
```

## Pull Request Run

The next section is the snyk run on pull request. There is not much to change here but it could be set to run on pull request, push, and commit. Here you can see the snyk token is used. This is the token that allows github to call upon snyk to run the scan publish the results.

```
snyk_run:
    name: Snyk Run (for PR)
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    
    steps:
      - name: Check out repository
        uses: actions/checkout@v3
      
      - name: Install Snyk and Run Snyk test
        run: |
          npm install -g snyk
          snyk test --all-projects --json > snyk_output.txt || true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## Cron Job Run

The last section is for the cron job. This is activated at the time specified above and then runs the snyk scan again. If there are still findings, there is a bug created in jira as shown with the action call at the end. This allows there to be bugs in a pull request and allows the day to get them fixed. If there is no fix made, then the bug is created to notify the user of the issue. 
The variables for ticket creation that can be modified are as follows: 
-	Token, host, project-key, and is_jira_enterprise should NOT be touched. They are static for this project.
-	Jira-issue-type: this is set to bug since most of the issues found will fall under that. However, this can be changed to any type of work item be it a user story, task, etc.
-	Jira-labels: This can be anything you want. It was set to eRegs and snyk to denote all of these bugs as  belonging to the eRegs project and from the snyk scan.
-	Jira-title-prefix: This is the prefix given to the ticket name so that it is also easily identifiable as a snyk bug. This can also be changed to anything.


```
snyk_nightly_run:  
      name: Snyk Nightly Run (for nightly cron with JIRA)
      runs-on: ubuntu-latest
      if: github.event_name == 'schedule'
      steps:
        - name: Check out repository
          uses: actions/checkout@v3
  
        - name: Install Snyk and Run Snyk test
          run: |
            npm install -g snyk
            snyk test --all-projects --json > snyk_output.txt || true
          env:
            SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
          
        - name: use the custom github  action to parse Snyk output
          uses: Enterprise-CMCS/macfc-security-scan-report@v2.7.4
          with:
              jira-token: ${{ secrets.JIRA_TOKEN }}
              jira-host: ${{ secrets.JIRA_HOST }}
              jira-project-key: 'EREGCSC'
              jira-issue-type: 'Bug'
              jira-labels: 'eRegs,snyk'
              jira-title-prefix: '[EREGCSC] - Snyk :'
              is_jira_enterprise: true
              #assign-jira-ticket-to: ''
              scan-output-path: 'snyk_output.txt'
              scan-type: 'snyk'
```

