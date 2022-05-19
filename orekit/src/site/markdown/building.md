<!--- Copyright 2002-2021 CS GROUP
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->

# Building Orekit Tutorials

Orekit Tutorials can be built from source using several different tools.

All these tools are Java based and can run on many different operating
systems, including Unix, GNU/Linux, Windows and Mac OS X. Some GNU/Linux
distributions provide these tools in their packages repositories.

## Building with Maven 3

[Maven](http://maven.apache.org/) is a build tool that goes far beyond
simply compiling and packaging a product. It is also able to resolve
dependencies (including downloading the appropriate versions from the public
repositories), to run automated tests, to launch various checking tools and
to create a web site for a project. It runs on any platform supporting Java.

For systems not providing maven as a package, maven can be
[downloaded](http://maven.apache.org/download.cgi) from its site at the
Apache Software Foundation. This site also explains the
installation procedure.

As with all maven enabled projects, building official released versions of
Orekit Tutorials is straightforward (see below for the special case of development versions),
simply run:

    mvn compile


This command should always work for released Orekit Tutorials versions as they
always depend only on released Orekit & Hipparchus versions. Maven knows how
to download the pre-built binary for released Hipparchus versions.
The previous command may not work for development Orekit Tutorials versions as they
may depend on unreleased Orekit or Hipparchus versions. Maven cannot download
pre-built binaries for unreleased Orekit or Hipparchus versions as none are
publicly available. In this case the command above will end with an error message
like:

    [ERROR] Failed to execute goal on project orekit-tutorials: Could not resolve dependencies for project org.orekit:orekit-tutorials:jar:X.Y-SNAPSHOT: Could not find artifact org.orekit:orekit:jar:X.Y-SNAPSHOT

In this case, you should build the missing Orekit or Hipparchus artifact and
install it in your local maven repository beforehand. This is done by cloning
the Hipparchus source from Hipparchus git repository at GitHub in some
temporary folder and install it with maven. This is done by
running the commands below (using Linux command syntax):

* Orekit:
    git clone https://gitlab.orekit.org/orekit/orekit.git
	git branch develop
    cd orekit
    mvn install

* Hipparchus:
    git clone https://github.com/Hipparchus-Math/hipparchus.git
    cd hipparchus
    mvn install

Once the Orekit & Hipparchus development versions has been installed locally using
the previous commands, you can delete the cloned folder if you want. You can then
attempt again the mvn command at Orekit Tutorials level, this time it should succeed as the
necessary artifact is now locally available.

If you need to configure a proxy server for dependencies retrieval, see
the [Guide to using proxies](http://maven.apache.org/guides/mini/guide-proxies.html)
page at the maven site.

For other commands like generating the site, or generating the
[checkstyle](http://checkstyle.sourceforge.net/),
[spotbugs](https://spotbugs.github.io/) see the maven
plugins documentation at [maven site](http://maven.apache.org/plugins/index.html).

## Building with Eclipse

[Eclipse](http://www.eclipse.org/) is a very rich Integrated Development
Environment (IDE). It is a huge product and not a simple build tool.

For systems not providing eclipse as a package, it can be downloaded from its
site at the [Eclipse Foundation](http://www.eclipse.org/downloads/).

The simplest way to use Orekit Tutorials with Eclipse is to follow these steps:

  * using your operating system tools, unpack the source distribution directly
    inside your Eclipse workspace. The source distribution file name has a name
    of the form orekit-tutorials-x.y-sources.zip where x.y is the version number. Unpacking
    this zip file should create a folder of the form orekit-tutorials-x.y in your workspace.

  * using Eclipse, import the project by selecting in the top level "File" menu
    the entry "Import..."

  * in the wizard that should appear, select "Maven -> Existing Maven Projects"

  * select the folder you just created in your workspace by unpacking the
    source distribution. The "pom.xml" file describing the project will be
    automatically selected. Click finish

The Orekit Tutorials library should be configured automatically, including the dependency
to the underlying mathematical library.

Now you have an orekit-tutorials-x.y project in you workspace, and you can create your
own application projects that will depend on the Orekit Turotials project.

You can also check everything works correctly by running one of the example tutorial.
