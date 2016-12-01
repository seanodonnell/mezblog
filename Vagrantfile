# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "app1.mezblog.odonnell.nu"
  config.vm.network :private_network, ip: "172.16.0.105" 
  config.vm.provision "shell", path: "bootstrap.sh", args: "app1.mezblog.odonnell.nu"
  config.vm.provision :host_shell do |host_shell|
      host_shell.inline = 'fab gen_keys:minion_name=app1.mezblog.odonnell.nu -H 172.16.0.155 -u root'
  end

  config.vm.provision :host_shell do |host_shell|
      host_shell.inline = 'fab preseed -H app1.mezblog.odonnell.nu -u vagrant'
  end
  config.vm.provision :host_shell do |host_shell|
      host_shell.inline = 'fab preseed -H app1.mezblog.odonnell.nu -u vagrant'
  end
  
  config.vm.provision :host_shell do |host_shell|
      host_shell.inline = 'fab postseed -H app1.mezblog.odonnell.nu -u vagrant'
  end

  config.vm.provision :salt do |salt|
    salt.run_highstate = true
  end

  config.vm.provision :host_shell do |host_shell|
      host_shell.inline = 'fab loaduserkey -H app1.mezblog.odonnell.nu -u vagrant'
  end

  config.vm.provision :host_shell do |host_shell|
      host_shell.inline = './release-vagrant.sh True'
  end


  config.vm.provision :shell, :inline => "sudo nginx restart", run: "always"
  config.vm.provision :shell, :inline => "sudo service uwsgi start", run: "always"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 512 
  end
end
