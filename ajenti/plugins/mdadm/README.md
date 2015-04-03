The plugin for Ajenti is free software licensed under version 3 or later 
of the GNU Affero General Public License. The plugin is maintained and 
copyrighted to Marc Bertens.
 
The plugin is intended to maintain the mdadm devices. Certain actions 
may cause that the system becomes unstable. There is put in a lot of 
care in the behaviour of the plugin, even so there is no guarantee on 
bad behaviour of the plugin or users. Therefore always make sure that 
you known what your doing and have backups of the devices your maintaining.

Features;
* Create new MD devices, based on available partions.
* Show details of the active MD devices.
* Show details of storage device attached to the MD device.
* Fail a storage device in an active MD device.
* Remove a failed storage device.
* Add spare storage device in an active MD device. When a storage device 
  is all ready failed will will become active directly, synchronization 
  is done automatically.
* Stop an existing MD device.
* Process indicator on checking, re-syncing and rebuilding.

* Widget; Show current status of the active MD devices.
* Widget; Process indicator on checking, re-syncing and rebuilding.
	
