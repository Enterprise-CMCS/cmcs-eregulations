# Snyk Scan

The snyk-test.yml script is located in the .github/workflows. This document outlines the parts of the file that are modifiable and the controls that are located within. This document has 2 actions within. First is the regular snyk scan that runs on pull request, and the second is a cron job snyk scan and jira ticket creation.

## Pull Request or Cron Job

At the top, the document checks to see if a pull request was done on the main branch or if it’s the set time for the cron job. The branch can be changed to whichever branch needs testing however, the deployment will also have to be done to that branch. The cron job will run at midnight EST meaning that if you put ‘04***’, that is 4am in a different time zone but midnight here.

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
    •	Username, token, host, project-key, and is_jira_enterprise should NOT be touched. They are static for this project.
    •	Jira-issue-type: this is set to bug since most of the issues found will fall under that. However, this can be changed to any type of work item be it a user story, task, etc.
    •	Jira-labels: This can be anything you want. It was set to eRegs and snyk to denote all of these bugs as  belonging to the eRegs project and from the snyk scan.
    •	Jira-title-prefix: This is the prefix given to the ticket name so that it is also easily identifiable as a snyk bug. This can also be changed to anything.


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
          uses: Enterprise-CMCS/macfc-security-scan-report@v2.7.0
          with:
              jira-username: ${{ secrets.JIRA_USERNAME }}
              jira-token: ${{ secrets.JIRA_TOKEN_AT }}
              jira-host: ${{ secrets.JIRA_HOST_NAME }}
              jira-project-key: 'EREGCSC'
              jira-issue-type: 'Bug'
              jira-labels: 'eRegs,snyk'
              jira-title-prefix: '[EREGCSC] - Snyk :'
              is_jira_enterprise: true
              #assign-jira-ticket-to: ''
              scan-output-path: 'snyk_output.txt'
              scan-type: 'snyk'
```

