<template>
  <div :style="{ width: width + 'px', height: height + 'px'}">
    <svg ref='svg' height='100%' width='100%'/>
  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'Chart',
  props: ['graph', 'graphLastUpdated'],
  data() {
    return {
      count: 0,
      forceProperties: {
        center: {
          x: 0.5,
          y: 0.5,
        },
        charge: {
          strength: -1000,
        },
        link: {
          distance: 150,
        },
      },
      lastUpdated: this.graphLastUpdated,
      nodeProperties: {
        minSize: 3,
      },
      selections: {},
      simulation: null,
      height: 3 * window.innerHeight / 4,
      width: window.innerWidth,
    };
  },
  mounted() {
    console.log(this.graph);
    // initialize interactions
    const zoom = d3.zoom().on('zoom', this.zoom);

    // initialize selections
    this.selections.svg = d3.select(this.$el.querySelector('svg')).call(zoom);
    this.selections.graph = this.selections.svg.append('g').attr('id', 'graph-group');
    this.selections.links = this.selections.graph.append('g').attr('id', 'link-group');
    this.selections.nodes = this.selections.graph.append('g').attr('id', 'node-group');

    // initialize simulation
    this.initializeSimulation();
  },
  methods: {
    clearGraph() {
      // clean up old nodes
      d3.selectAll('.link').remove();
      d3.selectAll('.node').remove();
    },
    drag(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    },
    dragStart(d) {
      if (!d3.event.active) this.simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    },
    dragEnd(d) {
      if (!d3.event.active) this.simulation.alphaTarget(0);
    },
    initializeSimulation() {
      this.simulation = d3.forceSimulation()
        .force('charge', d3.forceManyBody())
        .force('link', d3.forceLink())
        .force('center', d3.forceCenter())
        .on('tick', this.tick);

      this.updateForces();
    },
    tick() {
      let linkTransform;
      if (this.graph.multigraph) {
        linkTransform = d => 'M ' + d.source.x + ' ' + d.source.y + ' S ' + (d.target.x + d.offset) + ' ' + (d.target.y - d.offset) + ' ' + d.target.x + ' ' + d.target.y;
      } else {
        linkTransform = d => 'M' + d.source.x + ',' + d.source.y + ' L' + d.target.x + ',' + d.target.y;
      }
      const nodeTransform = d => 'translate(' + d.x + ',' + d.y + ')';
      const nodeTextColor = (d) => {
        if (d.degree > 0) {
          const windowArea = this.height * this.width;
          const svgArea = (2 * this.nodeProperties.minSize * d.degree) ** 2;
          const ratio = windowArea / svgArea;
          if (ratio > 10) {
            return 'white';
          }
        }
        return 'black';
      };

      this.selections.links.selectAll('.link').attr('d', linkTransform);
      this.selections.nodes.selectAll('.node').attr('transform', nodeTransform);
      this.selections.nodes.selectAll('text').attr('color', nodeTextColor);
    },
    updateForces() {
      this.simulation.force('center')
        .x(this.width * this.forceProperties.center.x)
        .y(this.height * this.forceProperties.center.y);
      this.simulation.force('charge')
        .strength(this.forceProperties.charge.strength);
      this.simulation.force('link')
        .id(d => d.id)
        .distance(this.forceProperties.link.distance);

      this.simulation.restart();
    },
    updateGraph() {
      // add nodes and links to graph
      this.simulation
        .nodes(this.graph.getNodes())
        .force('link')
          .links(this.graph.getLinks());

      // add links to DOM
      this.selections.links.selectAll('#link-group')
        .data(this.simulation.force('link').links())
        .join(
          enter => enter.append('path')
            .attr('class', 'link'),
        );

      // add nodes to DOM
      this.selections.nodes.selectAll('#node-group')
        .data(this.simulation.nodes())
        .join(
          enter => enter.append('g')
              .attr('class', 'node'),
        )
        .call(
          d3.drag()
            .on('start', this.dragStart)
            .on('drag', this.drag)
            .on('end', this.dragEnd),
        );

      // add node indicators
      this.selections.nodes.selectAll('.node')
        .append('circle')
          .attr('id', d => d.getId())
          .attr('r', (d) => {
            if (this.graph.connection === 'collaboration'
              || this.graph.multigraph
                || d.degree === 0
                  || !d.degree) {
              return this.nodeProperties.minSize;
            }
            if (d.degree > 49) {
              return this.forceProperties.link.distance - this.nodeProperties.minSize;
            }
            return this.nodeProperties.minSize * d.degree;
          })
          .attr('class', d => d.data.type);

      // add node labels
      this.selections.nodes.selectAll('.node')
        .append('text')
            .text(d => d.data.name)
            .attr('x', 6)
            .attr('y', 3);

      this.simulation.restart();
    },
    zoom() {
      this.selections.graph.attr('transform', d3.event.transform);
    },
  },
  watch: {
    graph: {
      handler() {
        this.initializeSimulation();
      },
    },
    graphLastUpdated: {
      handler() {
        this.clearGraph();
        this.updateGraph();
      },
    },
  },
};
</script>

<style>

circle.artist {
  fill: cadetblue;
}

circle.member {
  fill: cadetblue;
}

circle.group {
  fill: orange;
}

circle.label {
  fill: fuchsia;
}

circle.master {
  fill: darkorchid;
}

circle.release {
  fill: red;
}

.link {
  fill: none;
  stroke: #ccc;
}

.node:hover text {
  display: inline;
}

.popover {
  z-index: 10;
}

circle:focus {
  outline: 0;
}

</style>
