Set up to create UML diagrams:

1) Install Java

Check whether Java is already installed:

java -version

PlantUML requires Java, minimum version 8.

On macOS, a common install path is Homebrew:

brew install openjdk

Then re-open your teAMinal and run:

java -version
2) Install VS Code PlantUML extension

In VS Code, install the extension named PlantUML by jebbs

3) Install Graphviz

PlantUML’s docs say Graphviz is needed only for some diagrams, and PlantUML uses Graphviz/dot by default for layouts such as class and use-case style diagrams.

On macOS:

brew install graphviz

Then verify:

dot -V