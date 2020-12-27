# Ansible Collection - irom77.azure

- ansible-doc irom77.azure.azure_tags

# Requirements

- Ansible >= 2.9
- Python >= 3.6

# Example usage

See examples directory, and example of `var_files` provider below

```
azure_provider_test:
  tgs: creator: me
  client_id: ***
  subscription_id: ***
  tenant: ***
  secret: !vault |
          $ANSIBLE_VAULT;1.1;AES256
```

```
$ ansible-galaxy collection install irom77.azure
Starting galaxy collection install process
Process install dependency map
Starting collection install process
Installing 'irom77.azure:1.0.2' to '/home/docker/.ansible/collections/ansible_collections/irom77/azure'
Downloading https://galaxy.ansible.com/download/irom77-azure-1.0.2.tar.gz to /home/docker/.ansible/tmp/ansible-local-26771gdxkwujn/tmp6nsk53ax
irom77.azure (1.0.2) was installed successfully

$ ansible-playbook mod_test_azure_tags.yml --ask-vault-pass
Vault password: 
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Test azure_tags module] *************************************************************************************************************************************************************
TASK [Gathering Facts] ********************************************************************************************************************************************************************ok: [localhost]

TASK [Pull tags] **************************************************************************************************************************************************************************changed: [localhost]

TASK [debug] ******************************************************************************************************************************************************************************ok: [localhost] => {
    "addresses": {
        "changed": true,
        "debug_msg": "tgs:applicationname:awx applicationname:jenkins",
        "failed": false,
        "meta": [
            "10.12.9.41",
            "10.12.9.43"
        ]
    }
}

PLAY RECAP ********************************************************************************************************************************************************************************localhost                  : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

```
