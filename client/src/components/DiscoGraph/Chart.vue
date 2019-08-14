<template>
  <div :style="{ width: width + 'px', height: height + 'px'}">
    <svg ref='svg' height='100%' width='100%'/>
  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'Chart',
  props: ['graphData', 'nodeData', 'parameters'],
  data() {
    return {
      forceProperties: {
        center: {
          x: 0.5,
          y: 0.5,
        },
        charge: {
          strength: -500,
        },
        link: {
          distance: 150,
        },
      },
      graph: this.graphData,
      nodeDetails: this.nodeData,
      selections: {},
      simulation: null,
      height: 3 * window.innerHeight / 4,
      width: window.innerWidth,
    };
  },
  mounted() {
    // initialize interactions
    const zoom = d3.zoom().on('zoom', this.zoom);
    console.log(this.graph);

    // initialize selections
    this.selections.svg = d3.select(this.$el.querySelector('svg')).call(zoom);
    this.selections.graph = this.selections.svg.append('g').attr('id', 'graph-group');
    this.selections.links = this.selections.graph.append('g').attr('id', 'link-group');
    this.selections.nodes = this.selections.graph.append('g').attr('id', 'node-group');

    // initialize simulation
    this.simulation = d3.forceSimulation()
      .force('charge', d3.forceManyBody())
      .force('link', d3.forceLink())
      .force('center', d3.forceCenter())
      .on('tick', this.tick);

    // pass component data to update DOM
    this.updateForces();
    this.updateData();
  },
  methods: {
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
    showPopover(node) {
      const nodeData = {
        id: node.id,
        type: node.type,
      };
      console.log(nodeData);
      // this.$emit('getNodeData', nodeData);
      // this.$nextTick(() => {
      //   this.selections.popover = this.selections.nodes.append('g').attr('class', 'popover');
      //   this.selections.popover.append('rect')
      //       .attr('class', 'popover')
      //       .attr('fill', 'white')
      //       .attr('stroke', 'rgb(0, 0, 0)')
      //       .attr('height', 150)
      //       .attr('width', 150)
      //       .attr('x', node.x)
      //       .attr('y', node.y);
      //   console.log('test');
      //   console.log(this.nodeDetails);
      //   this.selections.popover.append('text')
      //       .text(node.name)
      //       .attr('class', 'popover')
      //       .attr('x', node.x)
      //       .attr('y', node.y + 20);
      //   this.selections.popover.append('text')
      //       .text(this.nodeDetails.uri)
      //       .attr('class', 'popover')
      //       .attr('x', node.x)
      //       .attr('y', node.y + 40);
      //   console.log(this.nodeDetails.urls);
      //   if (this.nodeDetails.urls) {
      //     for (let i = 0; i < this.nodeDetails.urls.length; i += 1) {
      //         this.selections.popover.append('text')
      //             .text(this.nodeDetails.urls[i])
      //             .attr('class', 'popover')
      //             .attr('x', node.x)
      //             .attr('y', node.y + 40 * (i + 1));
      //     }
      //   }
      // });
    },
    tick() {
      let linkTransform;
      if (this.graph.multigraph) {
        linkTransform = d => 'M ' + d.source.x + ' ' + d.source.y + ' S ' + (d.target.x + d.offset) + ' ' + (d.target.y - d.offset) + ' ' + d.target.x + ' ' + d.target.y;
      } else {
        linkTransform = d => 'M' + d.source.x + ',' + d.source.y + ' L' + d.target.x + ',' + d.target.y;
      }
      const nodeTransform = d => 'translate(' + d.x + ',' + d.y + ')';

      this.selections.links.selectAll('.link').attr('d', linkTransform);
      this.selections.nodes.selectAll('.node').attr('transform', nodeTransform);
    },
    updateData() {
      // add nodes and links to graph
      this.simulation
        .nodes(this.graph.nodes)
        .force('link')
          .links(this.graph.links);

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
          .attr('id', d => d.type + '_' + d.id)
          .attr('r', (d) => {
            if (this.parameters.sourceType !== this.parameters.targetType) {
              return 3;
            }
            if (d.degree > 49) {
              return 147;
            }
            if (d.degree === 0 || !d.degree) {
              return 3;
            }
            return 3 * d.degree;
          })
          .attr('class', d => d.type)
        .on('click', (d) => {
          this.selections.svg.selectAll('.popover').remove();
          this.showPopover(d);
        })
        .on('blur', () => {
          this.selections.svg.selectAll('.popover').remove();
        });

      // add node labels
      this.selections.nodes.selectAll('.node')
        .append('text')
            .text(d => d.name)
            .attr('x', 6)
            .attr('y', 3);

      this.simulation.restart();
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
    zoom() {
      this.selections.graph.attr('transform', d3.event.transform);
    },
  },
  updated() {
    this.updateData();
  },
  watch: {
    data: {
      handler(newData) {
        this.updateData();
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
