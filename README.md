# x10

Updates to the x10 code to access heyu via the ssh command to another server running heyu.  This gets around some of the issues when running Home Assistant within HAOS.

Add the following to configuration.yaml

    x10:
        use_ssh: true
        ssh_host: server
        ssh_username: user
        ssh_password: password
        devices: 
            - id: B1
              type: light
              name: "Friendly Name"

On the roadmap:
  type: sensor
  type: appliance
