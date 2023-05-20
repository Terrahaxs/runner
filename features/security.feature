Feature: runner is security features
    Background:
        Given a worker.request payload
        And a mocked terrahaxs api

    Scenario: runner doesn't execute commands with an invalid signature
        Given an invalid signature
        When I run the runner
        Then a InvalidSignatureError is raised

    Scenario: runner doesn't execute commands if org is not allow listed
        Given allowed orgs is Foo
        When I run the runner
        Then a OrgNotAllowedError is raised

    Scenario: runner doesn't execute commands if repo is not allow listed
        Given allowed orgs is *
        And allowed repos is Foo
        When I run the runner
        Then a RepoNotAllowedError is raised

    Scenario: runner doesn't execute commands if project is not allow listed
        Given allowed orgs is *
        And allowed repos is *
        And allowed projects is Foo
        When I run the runner
        Then a ProjectNotAllowedError is raised