

<div align="center">
  <h1>TerraFirmaGreg - Kube Package Manager</h1>
  
  ![banner](https://github.com/glitchplaysgames714/tfg-kpm/blob/main/.assets/banner.png?raw=true)

  <p align="center">
    <a href="https://github.com/glitchplaysgames714/Modpack-Modern/wiki">Developer docs</a>
    ·
    <a href="https://github.com/TerraFirmaGreg-Team/Modpack-Modern/issues">Report Bugs</a>
  </p>
</div>


---
<h2 align="center"> What is TFG-KPM </h2>

Terrafirmagreg kube package manager "TFG-KPM" is a package management tool built for server owners to easily install compatability addons with kubejs.
TFG-KPM allows server owners to easily install uninstall and update packages.

**TFG-KPM currently only supports recipes and tags. more on this is in the FAQ.**

<h2 align="center">TFG-KPM vs. the Traditional Method</h2>

Using TFG-KPM over manually installing packages saves alot of time. 
most of the time TFG-KPM will install packages in arround 1 second and uninstall packages in arround 30 milliseconds.

<h2 align="center"> Installation </h2>

> [!IMPORTANT]
> TFG-KPM was developed with uv in mind.
> we will not patch issues that are caused by using other package managers

You can install TFG-KPM using [uv](https://github.com/astral-sh/uv):
```bash
# install with uv
uv tool install tfg-kpm
```

You may also install TFG-KPM using any other python package manager: (not recommended)
```bash
# install with pip
pip install tfg-kpm
```

<h2 align="center"> Usage </h2>

> [!CAUTION]
> Always ensure the package you're downloading can be **trusted**, otherwise malicious code may be executed on your device.

Type `tfg-kpm --help` to view a list of commands.
Type `tfg-kpm <COMMAND> --help` to view information about a command.

<details>

<summary>Example commands</summary>


**Installing a package:**

```bash
dexi install <author/repo> 
```

**Installing a package from a specific branch:**

```bash
dexi install --branch <branch> <author/repo> 
```

**Listing all packages:**

```bash
tfg-kpm list
```

**Uninstalling a package:**

```bash
tfg-kpm uninstall <package name>
```

</details>

<h2 align="center">External Credits and Special Thanks</h2>

HUGE thanks to [Caylies's Dexi](https://github.com/Caylies/DexI/) for the insperation
