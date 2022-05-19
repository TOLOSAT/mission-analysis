# Orekit Tutorials Release Guide

This release guide is largely inspired from [Orekit Release Guide](https://gitlab.orekit.org/orekit/orekit/blob/develop/src/site/markdown/release-guide.md).

Note that:
  * Orekit tutorials do not require a vote from Orekit PMC to be released;
  * A new version of the tutorials must be released after each new version of Orekit so that the version numbers are the same. 

## Prerequisites

* Obtain private key of the Orekit Signing Key, key id:
   `0802AB8C87B0B1AEC1C1C5871550FDBD6375C33B`

If you need help with this ask on the development section of the Orekit forum.

Use `mvn -ep` to generate an encrypted password for the Orekit Signing Key.

## Verify the status of develop branch

Before anything, check on the [continuous integration page](https://gitlab.orekit.org/orekit/orekit-tutorials/pipelines)
that everything is fine on develop branch.  

Also check on your local repository that the quality of develop branch is good: there should be no Maven, Java, Javadoc, Checkstyle and SpotBugs error or warning.
If not, fix the warnings and errors first!

To check on this inspect your local IDE for Checkstyle and Java errors.  
Then for SpotBugs, Java, Javadoc and Checkstyle inspection run:
  
    mvn clean javadoc:javadoc verify site

First look at the log of this command and verify there are no errors.

Then browse the generated site starting at page `./target/site/index.html` and check
Checkstyle and SpotBugs reports at the bottom of it.

## Prepare Git branch for release

Release will be performed on a dedicated branch, not directly on master or
develop branch.  
So a new branch must be created as follows and used for
everything else:

    git branch release-X.Y
    git checkout release-X.Y

## Update maven plugins versions

Release is a good opportunity to update the Maven plugins versions. They are all
gathered at one place, in a set of properties in `orekit-tutorials/pom.xml`:

    <!-- Project specific plugin versions -->
    <orekit-tutorials.spotbugs-maven-plugin.version>3.1.12</orekit-tutorials.spotbugs-maven-plugin.version>
    <orekit-tutorials.maven-changes-plugin.version>2.12.1</orekit-tutorials.maven-changes-plugin.version>
    <orekit-tutorials.maven-checkstyle-plugin.version>3.1.0</orekit-tutorials.maven-checkstyle-plugin.version>
    ...

You can find the latest version of the plugins using the search feature at
[http://search.maven.org/#search](http://search.maven.org/#search). The
properties name all follow the pattern `orekit-tutorials.some-plugin-name.version`, the
plugin name should be used in the web form to check for available versions.

Beware that in some cases, the latest version cannot be used due to
incompatibilities. For example when a plugin was not recently updated and
conflicts appear with newer versions of its dependencies.

Beware also that some plugins use configuration files that may need update too.
This is typically the case with `maven-checkstyle-plugin` and
`spotbugs-maven-plugin`. The `/checkstyle.xml` and
`/spotbugs-exclude-filter.xml` files may need to be checked.

Before committing these changes, you have to check that everything works. So
run the following command:

    mvn clean
    LANG=C mvn clean javadoc:javadoc site

If something goes wrong, either fix it by changing the plugin configuration or
roll back to an earlier version of the plugin.

Browse the generated site starting at page `target/site/index.html` and check
that everything is rendered properly.

When everything runs fine and the generated site is OK, then you can commit the
changes:

    git add pom.xml checkstyle.xml spotbugs-exclude-filter.xml
    git commit -m "Updated maven plugins versions."

## Updating changes.xml

Finalize the file `/src/changes/changes.xml`

The release date and description, which are often only set to `TBD` during development, must be set to appropriate values.

Replace the `TBD` description with a text describing the version released by listing the major features introduced by
the version etc. (see examples in descriptions of former versions).

Commit the `changes.xml` file.

    git add src/changes/changes.xml
    git commit -m "Updated changes.xml for official release."                                                        

## Change library version number

The `pom.xml` file contains the version number of the library. During
development, this version number has the form `X.Y-SNAPSHOT`. For release, the
`-SNAPSHOT` part must be removed.

If you are releasing the tutorials it means a new version of Orekit was just released.  
Therefore you should also change the Orekit version number in the `orekit.version` variable.  
From:

    <orekit-tutorials.orekit.version>X.Y-SNAPSHOT</orekit-tutorials.orekit.version>
To:

    <orekit-tutorials.orekit.version>X.Y</orekit-tutorials.orekit.version>

Commit the change:

    git add pom.xml
    git commit -m "Dropped -SNAPSHOT in version number for official release."

## Tag and sign the git repository

When all previous steps have been performed, the local git repository holds the
final state of the sources and build files for the release.  
It must be tagged and the tag must be signed.  
Tagging and signing is done using the following command:

    git tag X.Y -s -u 0802AB8C87B0B1AEC1C1C5871550FDBD6375C33B -m "Version X.Y."

The tag should be verified using command:

    git tag -v X.Y

## Pushing the branch and the tag

When the tag is ready, the branch and the tag must be pushed to Gitlab so everyone can review it:

    git push --tags origin release-X.Y

Wait for the [continuous integration job](https://gitlab.orekit.org/orekit/orekit-tutorials/pipelines) to run and check that everything works fine on branch `release-X.Y`.

## Maven site

The Maven site is generated locally using:

    LANG=C mvn clean site
The Maven site part of the Orekit website is automatically updated on the hosting platform when work is
merged into branches `develop`, `release-*` or `master`.

## Generating signed artifacts locally

Contrary to Orekit library, the Orekit Tutorials artifacts are not pushed on Sonatype OSS site.  
The artifacts only need to be generated locally and uploaded on the Gitlab forge afterwards.
To generate the signed artifacts (and the site again) locally run:

    mvn clean verify site install -Prelease

During the generation, Maven will trigger gpg which will ask the user for the pass phrase to access the signing key.  
Maven didn’t prompt for me, so I had to add `-Dgpg.passphrase=[passphrase]`

Once the command ends, check that your `./target` directory contains the expected artifacts with associated signatures and checksums:

- orekit-tutorials-X.Y.pom
- orekit-tutorials-X.Y.jar
- orekit-tutorials-X.Y-sources.jar
- orekit-tutorials-X.Y-javadoc.jar

The signature and checksum files have similar names with added extensions `.asc`.


## Merge release branch into master branch

Merge the `release-X.Y` branch into the `master` branch to include any changes made.
The master branch always contains the latest release of the library.

    git checkout master
    git merge --no-ff release-X.Y

## Merge master branch into develop branch

Merge the updated `master` branch into the `develop` branch to include any changes made.

    git checkout develop
    git merge --no-ff master

## Prepare next development cycle in develop branch

Update the version numbers on `develop` branch to prepare for the next development cycle.  
Edit `pom.xml` versions (both Orekit tutorials and Orekit variable) to SNAPSHOT and make space in the change log in `./changes/changes.xml` for new changes.  
Then commit and push.

## Upload artifacts to gitlab

In the Gitlab forge, navigate to Self > Settings > Access Tokens. Enter a name, date, and check the
“api” box, then click “Create personal access token”.  
Copy the token into the following command:

    for f in $( ls target/orekit-tutorials-X.Y*.jar{,.asc} ) ; do
        curl --request POST --header "PRIVATE-TOKEN: <token>" --form "file=@$f" \
            https://gitlab.orekit.org/api/v4/projects/35/uploads
    done

Copy the URLs that are printed.

Next, navigate to Projects > Orekit > Repository > Tags. Find the X.Y tag and
click the edit button to enter release notes. Paste the URLs copied from the
step above.

Navigate to Projects > Orekit > Releases and make sure it looks nice.

## Update Orekit test website

Several edits need to be made to the Orekit website. Fetch the current code:

    git clone https://gitlab.orekit.org/orekit/website-2015
    
Switch to `develop` branch. This is the branch that will generate the "test" website.

Edit `_data/orekit-tutorials/versions.yml` by adding the new version X.Y to the list.

Edit `download/.htaccess` and replace the URL of of the zipped archive of the tutorials with the one given by Gitlab in Repository > Tags > X.Y


Wait for the [continuous integration](https://gitlab.orekit.org/orekit/website-2015/pipelines) job to deploy the test website.  
Then go to the [Orekit test website](https://test.orekit.org/) and make sure that everything looks nice and that the links work.

## Update Orekit official website

Switch to `master` branch. This is the branch that will generate the "official" website.  
Merge `develop` into `master`. 

    git checkout master
    git merge --no-ff develop
    
Wait for the [continuous integration](https://gitlab.orekit.org/orekit/website-2015/pipelines) job to deploy the official website.  
Then go to the [Orekit official website](https://orekit.org/) and make sure that everything looks nice and that the links work.


## Close X.Y milestone

In Gitlab, navigate to Projects > Orekit > Issues > Milestones.
If a line corresponding to the release X.Y exists click on “Close Milestone”.
