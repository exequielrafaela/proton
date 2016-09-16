local_mode true
chef_repo_path   File.expand_path('../' , __FILE__)

knife[:ssh_attribute] = "knife_zero.host"
knife[:use_sudo] = true
knife[:editor] = "vim"

## use specific key file to connect server instead of ssh_agent(use ssh_agent is set true by default).
# knife[:identity_file] = "~/.ssh/id_rsa"

## Attributes of node objects will be saved to json file.
## the automatic_attribute_whitelist option limits the attributes to be saved.
knife[:automatic_attribute_whitelist] = %w[
  fqdn
  os
  os_version
  hostname
  ipaddress
  roles
  recipes
  ipaddress
  platform
  platform_version
  cloud
  cloud_v2
  chef_packages
]