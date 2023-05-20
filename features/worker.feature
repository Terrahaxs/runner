Feature: runner works as expected
    Background:
        Given allowed orgs is *
        And allowed repos is *
        And allowed projects is *

    Scenario: runner returns failure state if step fails
        Given a worker.failed_step payload
        When I run the runner
        Then the result is failure


    Scenario: runner returns success state if no step fails
        Given a worker.request payload
        When I run the runner
        Then the result is success

    Scenario: runner support regex for allowed orgs
        Given a worker.request payload
        And allowed orgs is Terr.*
        When I run the runner
        Then the result is success
        
    Scenario: runner support multiple regex for allowed orgs
        Given a worker.request payload
        And allowed orgs is Git.*,Terr.*
        When I run the runner
        Then the result is success

    Scenario: runner runs all essential steps even if one fails
        Given a worker.failed_step payload
        When I run the runner
        Then the result is failure
        And there are 2 steps returned

    Scenario: worker is requires upgrade
        Given a worker.request payload
        And the worker is not up to date
        When I run the runner
        Then a UpgradeRunnerError is raised